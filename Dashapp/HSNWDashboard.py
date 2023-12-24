import numpy as np
import pandas as pd
import plotly.express as px
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ipywidgets as widgets
from IPython.display import display
from datetime import datetime, timedelta
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

reading_start_date = '01-01-2020'
DAYS_BEFORE_TEMP_1 = 200
DAYS_BEFORE_GEO = 7
HOURLY_DAYS_RANGE = 30
FIVE_MINS_READINGS_RANGE = 15
ROLLING_AVERAGE_WINDOW = 5
monroe_county = dict(lat=39.1690, lon=-86.5200)
heat_index_bands = [
        dict(type='rect', y0=-20, y1=-10, fillcolor='#05014a', opacity=0.2, name="Extreme Cold: Risk of frostbite and hypothermia. Dangerously cold conditions", layer='below'),
        dict(type='rect', y0=-10, y1=20, fillcolor='#00008B', opacity=0.2, name="Very Cold: Risk of frostbite. Prolonged exposure may lead to hypothermia", layer='below'),
        dict(type='rect', y0=20, y1=40, fillcolor='#0000CD', opacity=0.2, name="Cold: Risk of frostbite with prolonged exposure", layer='below'),
        dict(type='rect', y0=40, y1=60, fillcolor='#ADD8E6', opacity=0.2, name="Cool: Generally comfortable, but dress warmly in cool conditions", layer='below'),
        dict(type='rect', y0=60, y1=80, fillcolor='#00FF00', opacity=0.2, name="Comfortable: No discomfort expected", layer='below'),
        dict(type='rect', y0=80, y1=90, fillcolor='#FFFF00', opacity=0.2, name="Caution: Fatigue possible with prolonged exposure and physical activity", layer='below'),
        dict(type='rect', y0=90, y1=105, fillcolor='#FFA500', opacity=0.2, name="Extreme Caution: Heat cramps and heat exhaustion possible with prolonged exposure and physical activity", layer='below'),
        dict(type='rect', y0=105, y1=130, fillcolor='#FF0000', opacity=0.2, name="Danger: Heat stroke, heat cramps, and heat exhaustion likely with prolonged exposure and physical activity", layer='below'),
        dict(type='rect', y0=130, y1=1000, fillcolor='#8b0000', opacity=0.2, name="Extreme Danger: Heat stroke highly likely. Dangerously hot conditions", layer='below'),
    ]

readings = pd.read_csv("sensor_readings.csv", header=None, usecols=[1, 2, 3, 4, 6], names = ["Date", "Temperature", "Rel Humidity", "Dew Point", "Sensor Id"])
sensors = pd.read_csv("sensors.csv", header=None, usecols = [0, 1, 4, 6, 7], names = ["Sensor Id", "Name", "Location", "Latitude", "Longitude"])
readings["Date"] = pd.to_datetime(readings["Date"])

readings_day = readings.groupby([readings['Date'].dt.date, readings["Sensor Id"]]).agg({"Temperature":["mean", "max", "min"],
                                    "Rel Humidity":["mean", "max", "min"],
                                    "Dew Point":["mean", "max", "min"]}).droplevel(axis=1, level=[1]).reset_index()
readings_day.columns = ["Date", "Sensor Id", "Temperature_mean", "Temperature_max", "Temperature_min", "Rel Humidity_mean", "Rel Humidity_max", "Rel Humidity_min", "Dew Point_mean", "Dew Point_max", "Dew Point_min"]

sensor_locations = dict(zip(sensors["Sensor Id"], sensors["Location"]))
# readings_mean = readings_mean[readings_mean["Date"] >= datetime.strptime(reading_start_date, '%m-%d-%Y').date()]

# Get the sensor subset
sensor_subset = pd.merge(
    readings.groupby(["Sensor Id"]).agg({"Date": ["min", "max"]}).droplevel(level=[0], axis=1).reset_index().sort_values(by = ["max"], ascending=[False]),
    sensors, on = "Sensor Id").drop_duplicates(subset=["Latitude", "Longitude"]).sort_values(by = "Location")[["Sensor Id", "Location"]]
sensor_subset.columns = ["value", "label"]
sensor_subset_as_options = sensor_subset.to_dict('records')


app = dash.Dash(__name__)


@app.callback(
    Output('date-picker-temperature-1', 'end_date'),
    Input('sel-duration-temperature-1', 'value'),
    Input('date-picker-temperature-1', 'start_date'),
    Input('date-picker-temperature-1', 'end_date'),
)
def update_end_date_time_series(value, start_date, end_date):
    if value is None: value = '1'
    date_diff = datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")
    if value == '2' and date_diff.days > HOURLY_DAYS_RANGE:
        end_date = datetime.strftime(datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=HOURLY_DAYS_RANGE), '%Y-%m-%d')
    elif value == '3' and date_diff.days > FIVE_MINS_READINGS_RANGE:
        end_date = datetime.strftime(datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=FIVE_MINS_READINGS_RANGE), '%Y-%m-%d')
    return end_date


@app.callback(
    Output('Temperature-Chart', 'figure'),
    Input('sel-temperature-metric-1', 'value'),
    Input('sel-duration-temperature-1', 'value'),
    Input('sel-smoothen-temperature-1', 'value'),
    Input('date-picker-temperature-1', 'start_date'),
    Input('date-picker-temperature-1', 'end_date'),
    # Input('Temperature-Chart', 'relayoutData'),
)
def get_time_series(metric, duration, smoothen, start_date, end_date):
    readings_slice = None
    if duration is None: duration = '1'
    if metric is None: metric = '1'
    if smoothen is None: smoothen = '1'
    field_mean, field_name, label_name, label_value = get_metric_field_names(metric)

    # print("Out Data :", relayout_data)
    # if 'xaxis.range[0]' in relayout_data and 'xaxis.range[1]' in relayout_data:
    #     # Extract the range values from the relayout_data
    #     range_start = relayout_data['xaxis.range[0]']
    #     range_end = relayout_data['xaxis.range[1]']
    #
    #     # Do something with the range values
    #     print(f"Rangeslider event captured. Start: {range_start}, End: {range_end}")

    if duration == '1':
        readings_slice = readings_day.loc[(readings_day["Date"] >= datetime.strptime(start_date, '%Y-%m-%d').date())
                                           & (readings_day["Date"] <= datetime.strptime(end_date, '%Y-%m-%d').date())]
    elif duration == '2':
        date_diff = datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")
        if date_diff.days > HOURLY_DAYS_RANGE:
            end_date = datetime.strftime(datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=HOURLY_DAYS_RANGE), '%Y-%m-%d')
        readings_slice = readings.loc[(readings["Date"] >= datetime.strptime(start_date + " 00:00:00", '%Y-%m-%d %H:%M:%S'))
                                      & (readings["Date"] <= datetime.strptime(end_date + " 23:59:59", '%Y-%m-%d %H:%M:%S'))]
        readings_slice["Date"] = readings_slice["Date"].dt.strftime('%Y-%m-%d %H:00:00')

    elif duration == '3':
        date_diff = datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")
        if date_diff.days > FIVE_MINS_READINGS_RANGE:
            end_date = datetime.strftime(datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=FIVE_MINS_READINGS_RANGE), '%Y-%m-%d')
        readings_slice = readings.loc[(readings["Date"] >= datetime.strptime(start_date + " 00:00:00", '%Y-%m-%d %H:%M:%S'))
            & (readings["Date"] <= datetime.strptime(end_date + " 23:59:59", '%Y-%m-%d %H:%M:%S'))]
        # readings_slice = readings_slice.groupby([readings_slice['Date'], readings_slice["Sensor Id"]]) \
        #     .mean(numeric_only=True).reset_index()

    if duration == '2' or duration == '3':
        readings_slice = readings_slice.groupby([readings_slice['Date'], readings_slice["Sensor Id"]]).agg(
            {"Temperature": ["mean", "max", "min"],
             "Rel Humidity": ["mean", "max", "min"],
             "Dew Point": ["mean", "max", "min"]}).droplevel(axis=1, level=[1]).reset_index()
        readings_slice.columns = ["Date", "Sensor Id", "Temperature_mean", "Temperature_max", "Temperature_min",
                                  "Rel Humidity_mean", "Rel Humidity_max", "Rel Humidity_min", "Dew Point_mean",
                                  "Dew Point_max", "Dew Point_min"]

    if metric == '4':
        readings_slice["Heat Index_mean"] = readings_slice.apply(lambda row: get_heat_index(row), axis=1)

    if metric == '5':
        readings_slice["Humidex_mean"] = readings_slice.apply(lambda row: get_humidex(row), axis=1)

    if smoothen == '2':
        readings_slice[field_mean] = readings_slice[field_mean].rolling(window=ROLLING_AVERAGE_WINDOW).mean()

    readings_slice = readings_slice[["Date", "Sensor Id", field_mean]]
    readings_slice.columns = ["Date", "Sensor Id", field_name]

    unique_sensor_ids = list(np.sort(readings_day["Sensor Id"].unique()))
    fig = px.line()
    for sensor_id in unique_sensor_ids:
        df = readings_slice[readings_slice["Sensor Id"] == sensor_id]
        fig.add_scatter(x=df["Date"], y=df[field_name], mode='lines', name=sensor_locations[sensor_id])

    fig.update_layout(
        title=label_value,
        # plot_bgcolor='#FEFEFE',
        yaxis=dict(showline=True, linewidth=2, linecolor='darkgray'),
        xaxis=dict(
            showline=True,
            linewidth=2,
            linecolor='darkgray',
            # rangeselector=dict(
            #     buttons=list(
            #         [
            #             dict(count=1, label="1m", step="month", stepmode="backward"),
            #             dict(count=3, label="3m", step="month", stepmode="backward"),
            #             dict(count=6, label="6m", step="month", stepmode="backward"),
            #             dict(count=9, label="9m", step="month", stepmode="backward"),
            #             dict(count=1, label="YTD", step="year", stepmode="todate"),
            #             dict(count=1, label="1y", step="year", stepmode="backward"),
            #             dict(step="all"),
            #         ]
            #     ),
            #     x=1,  # Set x to 1 for right alignment
            #     xanchor='right',  # Use xanchor to specify right alignment
            #     y=1,
            #     yanchor='bottom'
            # ),
            # tickmode="array",
            # tickvals=readings_day["Date"],
            # #ticktext=["Jan", "Feb", "Mar", "Apr", "May"],
            rangeslider=dict(visible=True),
            type="date",
        ),
    )


    show_bands = True
    if show_bands and metric == '4':
        min_date = readings_slice["Date"].min()
        max_date = readings_slice["Date"].max()
        min_heat_index = readings_slice[field_name].min()
        max_heat_index = readings_slice[field_name].max()

        bands = [
            dict(type='rect', x0 = min_date, x1 = max_date, y0=40, y1=60, fillcolor='#ADD8E6', opacity=0.2, name="Cool: Generally comfortable, but dress warmly in cool conditions", layer='below'),
            dict(type='rect', x0 = min_date, x1 = max_date, y0=60, y1=80, fillcolor='#00FF00', opacity=0.2, name="Comfortable: No discomfort expected", layer='below'),
            dict(type='rect', x0 = min_date, x1 = max_date, y0=80, y1=90, fillcolor='#FFFF00', opacity=0.2, name="Caution: Fatigue possible with prolonged exposure and physical activity", layer='below'),
            dict(type='rect', x0 = min_date, x1 = max_date, y0=90, y1=105, fillcolor='#FFA500', opacity=0.2, name="Extreme Caution: Heat cramps and heat exhaustion possible with prolonged exposure and physical activity", layer='below'),
            dict(type='rect', x0 = min_date, x1 = max_date, y0=105, y1=130, fillcolor='#FF0000', opacity=0.2, name="Danger: Heat stroke, heat cramps, and heat exhaustion likely with prolonged exposure and physical activity", layer='below'),
            dict(type='rect', x0 = min_date, x1 = max_date, y0=130, y1=max_heat_index, fillcolor='#8b0000', opacity=0.2, name="Extreme Danger: Heat stroke highly likely. Dangerously hot conditions", layer='below'),
        ]

        for band in bands:
            fig.add_shape(band)
            # x = 20,
            # y = (band['y0'] + band['y1']) / 2,
            # fig.add_annotation(text="High Risk")

    fig.update_layout(showlegend=True, yaxis=dict(autorange=True, fixedrange=False), height = 750)
    return fig


@app.callback(
    Output('Deviation-Chart', 'figure'),
    Input('sel-deviation-metric-1', 'value'),
    Input('sel-duration-deviation-1', 'value'),
    Input('sel-smoothen-deviation-1', 'value'),
    Input('sel-baseline-deviation-1', 'value'),
    Input('date-picker-deviation-1', 'start_date'),
    Input('date-picker-deviation-1', 'end_date'),
)
def get_deviation_time_series(metric, duration, smoothen, baseline_sensor_id, start_date, end_date):
    readings_slice = None
    if duration is None: duration = '1'
    if metric is None: metric = '1'
    if smoothen is None: smoothen = '1'
    if baseline_sensor_id is None: baseline_sensor_id = sensor_subset_as_options[0]["value"]
    field_mean, field_name, label_name, label_value = get_metric_field_names(metric)

    if duration == '1':
        readings_slice = readings_day.loc[(readings_day["Date"] >= datetime.strptime(start_date, '%Y-%m-%d').date())
                                           & (readings_day["Date"] <= datetime.strptime(end_date, '%Y-%m-%d').date())]
    elif duration == '2':
        date_diff = datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")
        if date_diff.days > HOURLY_DAYS_RANGE:
            end_date = datetime.strftime(datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=HOURLY_DAYS_RANGE), '%Y-%m-%d')
        readings_slice = readings.loc[(readings["Date"] >= datetime.strptime(start_date + " 00:00:00", '%Y-%m-%d %H:%M:%S'))
                                      & (readings["Date"] <= datetime.strptime(end_date + " 23:59:59", '%Y-%m-%d %H:%M:%S'))]
        readings_slice["Date"] = readings_slice["Date"].dt.strftime('%Y-%m-%d %H:00:00')

    elif duration == '3':
        date_diff = datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")
        if date_diff.days > FIVE_MINS_READINGS_RANGE:
            end_date = datetime.strftime(datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=FIVE_MINS_READINGS_RANGE), '%Y-%m-%d')
        readings_slice = readings.loc[(readings["Date"] >= datetime.strptime(start_date + " 00:00:00", '%Y-%m-%d %H:%M:%S'))
            & (readings["Date"] <= datetime.strptime(end_date + " 23:59:59", '%Y-%m-%d %H:%M:%S'))]
        # readings_slice = readings_slice.groupby([readings_slice['Date'], readings_slice["Sensor Id"]]) \
        #     .mean(numeric_only=True).reset_index()

    if duration == '2' or duration == '3':
        readings_slice = readings_slice.groupby([readings_slice['Date'], readings_slice["Sensor Id"]]).agg(
            {"Temperature": ["mean", "max", "min"],
             "Rel Humidity": ["mean", "max", "min"],
             "Dew Point": ["mean", "max", "min"]}).droplevel(axis=1, level=[1]).reset_index()
        readings_slice.columns = ["Date", "Sensor Id", "Temperature_mean", "Temperature_max", "Temperature_min",
                                  "Rel Humidity_mean", "Rel Humidity_max", "Rel Humidity_min", "Dew Point_mean",
                                  "Dew Point_max", "Dew Point_min"]

    if metric == '4':
        readings_slice["Heat Index_mean"] = readings_slice.apply(lambda row: get_heat_index(row), axis=1)

    if metric == '5':
        readings_slice["Humidex_mean"] = readings_slice.apply(lambda row: get_humidex(row), axis=1)

    if smoothen == '2':
        readings_slice[field_mean] = readings_slice[field_mean].rolling(window=ROLLING_AVERAGE_WINDOW).mean()

    readings_slice = readings_slice[["Date", "Sensor Id", field_mean]]
    readings_slice.columns = ["Date", "Sensor Id", field_name]

    # Compute Deviation from the readings of the baseline sensor selected
    baseline_readings = readings_slice[readings_slice['Sensor Id'] == baseline_sensor_id]
    merged_readings = pd.merge(readings_slice, baseline_readings[['Date', field_name]], on='Date', suffixes=('', '_baseline'))
    merged_readings["Deviation"] = merged_readings[field_name] - merged_readings[field_name + "_baseline"]


    unique_sensor_ids = list(np.sort(readings_day["Sensor Id"].unique()))
    fig = px.line()
    for sensor_id in unique_sensor_ids:
        df = merged_readings[merged_readings["Sensor Id"] == sensor_id]
        fig.add_scatter(x=df["Date"], y=df["Deviation"], mode='lines', name=sensor_locations[sensor_id])

    fig.update_layout(
        title=label_value,
        # plot_bgcolor='#FEFEFE',
        yaxis=dict(showline=True, linewidth=2, linecolor='darkgray'),
        xaxis=dict(
            showline=True,
            linewidth=2,
            linecolor='darkgray',
            rangeslider=dict(visible=True),
            type="date",
        ),
    )

    fig.update_layout(yaxis=dict(autorange=True, fixedrange=False), height = 750)
    return fig


def get_spatial_view(metric):
    # if metric is None: metric = 1
    # field_mean, field_name, label_name, label_value = get_metric_field_names(metric)
    sensors_geo = readings_day.groupby("Sensor Id").agg({"Date": ["max"], "Temperature_mean": ["max"]})\
        .droplevel(axis=1,level=[1]).reset_index()
    sensors_geo = pd.merge(sensors_geo, sensors[sensors["Sensor Id"].isin(sensors_geo["Sensor Id"])], on="Sensor Id")
    sensors_geo.sort_values(by="Date", ascending=False, inplace=True)
    sensors_geo = sensors_geo[~sensors_geo.duplicated(subset=['Latitude', 'Longitude'])]
    sensors_geo["Size_col"] = 100
    sensors_geo.columns = ['Sensor Id', 'Date', 'Temperature', 'Name', 'Location', 'Latitude', 'Longitude', 'Size_col']
    fig = px.scatter_mapbox(
        sensors_geo,
        lat='Latitude',
        lon='Longitude',
        text='Location',
        size='Size_col', #Fixed Size
        color='Temperature',
        zoom=15,
        center=monroe_county,
        color_continuous_scale=px.colors.diverging.RdBu[::-1], #"Turbo",
        size_max=12,
        hover_name="Location",
        hover_data=dict(Temperature=':.2f',
                        Date=True,
                        Size_col = False,
                        Location = False,
                        Latitude = False,
                        Longitude = False)
    )
    fig.update_layout(title='Spatial View', mapbox_style="open-street-map", height = 750)
    return fig


def get_metric_field_names(metric):
    field_mean, field_name = "Temperature_mean", "Temperature"
    label_name, label_value = "Temperature", "Temperature"
    if metric == '2':
        field_mean, field_name = "Rel Humidity_mean", "Rel Humidity"
        label_name, label_value = "Rel Humidity", "Relative Humidity"
    elif metric == '3':
        field_mean, field_name = "Dew Point_mean", "Dew Point"
        label_name, label_value = "Dew Point", "Dew Point"
    elif metric == '4':
        field_mean, field_name = "Heat Index_mean", "Heat Index"
        label_name, label_value = "Heat Index", "Heat Index"
    return field_mean, field_name, label_name, label_value


@app.callback(
    Output('Temperature-Distribution', 'figure'),
    Input('sel-distribution-metric-1', 'value'),
    Input('date-picker-distribution-1', 'start_date'),
    Input('date-picker-distribution-1', 'end_date'),
)
def get_distribution(metric, start_date, end_date):
    readings_slice = readings_day.loc[(readings_day["Date"] >= datetime.strptime(start_date, '%Y-%m-%d').date())
                                      & (readings_day["Date"] <= datetime.strptime(end_date, '%Y-%m-%d').date())]
    if metric is None: metric = 1
    field_mean, field_name, label_name, label_value = get_metric_field_names(metric)
    if metric == '4':
        readings_slice["Heat Index_mean"] = readings_slice.apply(lambda row: get_heat_index(row), axis=1)

    if metric == '5':
        readings_slice["Humidex_mean"] = readings_slice.apply(lambda row: get_humidex(row), axis=1)

    readings_slice = readings_slice[["Date", "Sensor Id", field_mean]]
    readings_slice.columns = ["Date", "Sensor Id", field_name]
    readings_slice = pd.merge(readings_slice, sensors, on="Sensor Id")[["Date", "Sensor Id", field_name, "Location"]]

    fig = px.box(readings_slice, x='Location', y=field_name,
                 title=label_value + ' Comparison - Box Plot', labels={label_name: label_value}, color='Location')
    fig.update_layout(title=label_value + ' Distribution', height=750)
    return fig


@app.callback(
    Output('Compare-Metric-Past', 'figure'),
    Input('sel-compare-metric-1', 'value'),
    Input('date-picker-compare-1', 'start_date'),
    Input('date-picker-compare-1', 'end_date'),
)
def get_comparison(metric, start_date, end_date):
    start_date, end_date = format_date(start_date), format_date(end_date)
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    st_yr, st_mon, st_day = start_date.year, start_date.month, start_date.day
    en_yr, en_mon, en_day = end_date.year, end_date.month, end_date.day
    result_df = pd.DataFrame()
    for year in range(readings_day["Date"].min().year, readings_day["Date"].max().year + 1):
        from_date, to_date = datetime(year, st_mon, st_day).date(), datetime(year, en_mon, en_day).date()
        condition1, condition2 = readings_day["Date"] >= from_date, readings_day["Date"] <= to_date
        readings_slice = readings_day[condition1 & condition2].copy()
        readings_slice["Date Range"] = from_date.strftime('%d-%b-%Y') + " - " + to_date.strftime('%d-%b-%Y')
        readings_slice.drop(columns="Date", inplace=True)
        result_df = pd.concat([result_df, readings_slice])

    field_mean, field_name, label_name, label_value = get_metric_field_names(metric)
    if metric == '4':
        result_df["Heat Index_mean"] = result_df.apply(lambda row: get_heat_index(row), axis=1)

    if metric == '5':
        readings_slice["Humidex_mean"] = readings_slice.apply(lambda row: get_humidex(row), axis=1)

    result_df = result_df[["Date Range", "Sensor Id", field_mean]]
    result_df = result_df.groupby(["Date Range", "Sensor Id"]).agg({field_mean: "mean"}).reset_index()
    result_df.columns = ["Date Range", "Sensor Id", field_name]
    result_df = pd.merge(result_df, sensors, on="Sensor Id")
    result_df.sort_values(by="Date Range", ascending=False, inplace=True)
    result_df = result_df.drop_duplicates(subset=["Date Range", "Latitude", "Longitude"])
    result_df.sort_values(by="Date Range", inplace=True)

    fig = px.bar(result_df, x='Location', y=field_name, barmode='group',
                 title=label_value, labels={label_name: label_value}, color='Date Range')
    fig.update_layout(height=750)
    unique_locations = result_df['Location'].unique()
    min_value = result_df[field_name].min()
    min_value = (min_value if min_value < 0 else 0) - 5
    max_value = result_df[field_name].max()
    for i in range(1, len(unique_locations)):
        fig.add_shape(
            type='line',
            x0=i - 0.5,
            x1=i - 0.5,
            y0=min_value,
            y1=max_value,
            line=dict(color='black', width=1)
        )
    return fig


# @app.callback(
#     Output('Correlate-Metric', 'figure'),
#     Input('date-picker-compare-1', 'start_date'),
#     Input('date-picker-compare-1', 'end_date'),
# )
# def get_correlation(start_date, end_date):
#     readings_slice = readings_day.loc[(readings_day["Date"] >= datetime.strptime(start_date, '%Y-%m-%d').date())
#                                       & (readings_day["Date"] <= datetime.strptime(end_date, '%Y-%m-%d').date())]
#     fig = px.scatter_matrix(dimensions=[readings_slice['Temperature_mean'], readings_slice['Rel Humidity_mean'], readings_slice['Dew Point_mean']],
#                             color='Sensor Id', title='Scatter Matrix')
#     # fig = px.scatter_3d(readings_slice, x='Temperature_mean', y='Rel Humidity_mean', z='Dew Point_mean', color='Sensor Id',
#     #                     title='3D Scatter Plot by Sensor')
#     return fig


def get_heat_index(row):
    temperature, humidity = row["Temperature_mean"], row["Rel Humidity_mean"]
    c = [-42.379, 2.04901523, 10.14333127, -0.22475541, -6.83783e-3,
         -5.481717e-2, 1.22874e-3, 8.5282e-4, -1.99e-6]
    t2 = temperature ** 2
    r2 = humidity ** 2
    heat_index = c[0] + c[1]*temperature + c[2]*humidity + c[3]*temperature*humidity + c[4]*t2 + c[5]*r2 + \
                    c[6]*t2*humidity + c[7]*temperature*r2 + c[8]*t2*r2
    return heat_index


def get_humidex(row):
    temperature, dewpoint = row["Temperature_mean"], row["Dew Point_mean"]
    e = 6.11 * math.exp(5417.7530 * ((1 / 273.16) - (1 / dewpoint)))
    h = 0.5555 * (e - 10.0)
    temp_celsius = (temperature - 32) * 5/9
    humidex = temp_celsius + h
    return humidex


def format_date(str_date):
    index = str_date.find('T')
    if index != -1:
        str_date = str_date[0:index - 1]
    return str_date


# def get_heat_index_bands(min_date, max_date, min_heat_index, max_heat_index):
#     bands = []
#     for band in heat_index_bands:
#         if band["y0"] <= min_heat_index or band["y1"] < max_heat_index:


app.layout = html.Div([
    html.H1("Heat Sensor Network Data", style = {'font-family':'Arial','color':'blue', 'text-align':'center'}),
    html.Div([
            html.H2("Sensors & NWS Readings", style = {'font-family':'Arial', 'color':'darkred', 'padding-left':'20px'}),
            html.Div([
                    dcc.Dropdown(
                        id='sel-temperature-metric-1',
                        options=[{'label': 'Temperature', 'value': '1'},
                                 {'label': 'Relative Humidity', 'value': '2'},
                                 {'label': 'Dew Point', 'value': '3'},
                                 {'label': 'Heat Index', 'value': '4'},
                                 {'label': 'Humidex', 'value': '5'}],
                        value='1',
                        style={'font-family':'Arial', 'font-size':'11pt', 'width': '300px'},
                    ),
                    dcc.Dropdown(
                        id='sel-duration-temperature-1',
                        options=[{'label': 'Daily Average', 'value': '1'},
                                 {'label': 'Hourly Average', 'value': '2'},
                                 {'label': 'Every 5 Mins. Readings', 'value': '3'}],
                        value='1',
                        style={'font-family':'Arial', 'font-size':'11pt', 'width': '300px'},
                    ),
                    dcc.Dropdown(
                        id='sel-smoothen-temperature-1',
                        options=[{'label': 'Raw', 'value': '1'},
                                 {'label': 'Rolling Average', 'value': '2'}],
                        value='1',
                        style={'font-family':'Arial', 'font-size':'11pt', 'width': '300px'},
                    ),
                    dcc.DatePickerRange(
                            id='date-picker-temperature-1',
                            min_date_allowed=readings_day['Date'].min(),
                            max_date_allowed=readings_day['Date'].max(),
                            start_date=readings_day['Date'].max() - timedelta(days = DAYS_BEFORE_TEMP_1),
                            end_date=readings_day['Date'].max(),
                            display_format='DD-MMM-YYYY',
                            minimum_nights=0,
                            style={'font-family':'Arial', 'font-size':'11pt'},
                        ),
                    ], style={'padding': '10px', 'display': 'flex', 'justify-content': 'space-between'}),
                dcc.Graph(id='Temperature-Chart')
                #           figure=get_time_series('1', '1', '1', (readings_day["Date"].max() - timedelta(days=DAYS_BEFORE_TEMP_1)).strftime("%Y-%m-%d"),
                #                                   readings_day["Date"].max().strftime("%Y-%m-%d"))),
        ], style={
                    'backgroundColor': 'white',
                    'border': '1px solid darkgray',
                    'box-shadow': '3px 3px 3px rgba(0, 0, 0, 0.2)'
                }),
        html.Br(),
        html.Br(),
        html.Div([
            html.H2("Deviation", style={'font-family': 'Arial', 'color': 'darkred', 'padding-left': '20px'}),
            html.Div([
                dcc.Dropdown(
                    id='sel-deviation-metric-1',
                    options=[{'label': 'Temperature', 'value': '1'},
                             {'label': 'Relative Humidity', 'value': '2'},
                             {'label': 'Dew Point', 'value': '3'},
                             {'label': 'Heat Index', 'value': '4'},
                             {'label': 'Humidex', 'value': '5'}],
                    value='1',
                    style={'font-family':'Arial', 'font-size':'11pt', 'width': '300px'},
                ),
                dcc.Dropdown(
                    id='sel-duration-deviation-1',
                    options=[{'label': 'Daily Average', 'value': '1'},
                             {'label': 'Hourly Average', 'value': '2'},
                             {'label': 'Every 5 Mins. Readings', 'value': '3'}],
                    value='1',
                    style={'font-family':'Arial', 'font-size':'11pt', 'width': '300px'},
                ),
                dcc.Dropdown(
                    id='sel-smoothen-deviation-1',
                    options=[{'label': 'Raw', 'value': '1'},
                             {'label': 'Rolling Average', 'value': '2'}],
                    value='1',
                    style={'font-family':'Arial', 'font-size':'11pt', 'width': '300px'},
                ),
                dcc.Dropdown(
                    id='sel-baseline-deviation-1',
                    options=sensor_subset_as_options,
                    value=sensor_subset_as_options[0]["value"],
                    style={'font-family':'Arial', 'font-size':'11pt', 'width': '300px'},
                ),
                dcc.DatePickerRange(
                        id='date-picker-deviation-1',
                        min_date_allowed=readings_day['Date'].min(),
                        max_date_allowed=readings_day['Date'].max(),
                        start_date=readings_day['Date'].max() - timedelta(days = DAYS_BEFORE_TEMP_1),
                        end_date=readings_day['Date'].max(),
                        display_format='DD-MMM-YYYY',
                        minimum_nights=0,
                        style={'font-family':'Arial', 'font-size':'15px'},
                    ),
                ], style={'padding': '10px', 'display': 'flex', 'justify-content': 'space-between'}),
                dcc.Graph(id='Deviation-Chart')
                #           figure=get_deviation_time_series('1', '1', '1', sensor_subset_as_options[0]["value"], (readings_day["Date"].max() - timedelta(days=DAYS_BEFORE_TEMP_1)).strftime("%Y-%m-%d"),
                #                                   readings_day["Date"].max().strftime("%Y-%m-%d"))),
                ], style={
                    'backgroundColor': 'white',
                    'border': '1px solid darkgray',
                    'box-shadow': '3px 3px 3px rgba(0, 0, 0, 0.2)'
                }),
        html.Br(),
        html.Br(),
        html.Div([
            html.H2("Mean Temperature", style={'font-family': 'Arial', 'color': 'darkred', 'padding-left': '20px'}),
            dcc.Graph(id='Spatial-View-Chart',
                      figure=get_spatial_view('1')),
            ], style={
                    'backgroundColor': 'white',
                    'border': '1px solid darkgray',
                    'box-shadow': '3px 3px 3px rgba(0, 0, 0, 0.2)'
            }),
        html.Br(),
        html.Br(),
        html.Div([
        html.H2("Distribution", style={'font-family': 'Arial', 'color': 'darkred', 'padding-left': '20px'}),
            html.Div([
                dcc.Dropdown(
                    id='sel-distribution-metric-1',
                    options=[{'label': 'Temperature', 'value': '1'},
                             {'label': 'Relative Humidity', 'value': '2'},
                             {'label': 'Dew Point', 'value': '3'},
                             {'label': 'Heat Index', 'value': '4'},
                             {'label': 'Humidex', 'value': '5'}],
                    value='1',
                    style={'font-family':'Arial', 'width': '300px', 'font-size':'11pt'},
                ),
                dcc.DatePickerRange(
                        id='date-picker-distribution-1',
                        min_date_allowed=readings_day['Date'].min(),
                        max_date_allowed=readings_day['Date'].max(),
                        start_date=readings_day['Date'].max() - timedelta(days = DAYS_BEFORE_TEMP_1),
                        end_date=readings_day['Date'].max(),
                        display_format='DD-MMM-YYYY',
                        minimum_nights=0,
                        style={'font-family':'Arial', 'font-size':'11pt'},
                    ),
                ], style={'padding': '10px', 'display': 'flex', 'justify-content': 'space-between'}),
                dcc.Graph(id='Temperature-Distribution'),
                #           figure=get_distribution('1', (readings_day["Date"].max() - timedelta(days=DAYS_BEFORE_TEMP_1)).strftime("%Y-%m-%d"),
                #                                   readings_day["Date"].max().strftime("%Y-%m-%d"))),
            ], style={
                    'backgroundColor': 'white',
                    'border': '1px solid darkgray',
                    'box-shadow': '3px 3px 3px rgba(0, 0, 0, 0.2)'
            }),
        html.Br(),
        html.Br(),
        html.Div([
        html.H2("Compare to Past", style={'font-family': 'Arial', 'color': 'darkred', 'padding-left': '20px'}),
            html.Div([
                dcc.Dropdown(
                    id='sel-compare-metric-1',
                    options=[{'label': 'Temperature', 'value': '1'},
                             {'label': 'Relative Humidity', 'value': '2'},
                             {'label': 'Dew Point', 'value': '3'},
                             {'label': 'Heat Index', 'value': '4'},
                             {'label': 'Humidex', 'value': '5'}],
                    value='1',
                    style={'font-family':'Arial', 'width': '300px', 'font-size':'11pt'},
                ),
                dcc.DatePickerRange(
                        id='date-picker-compare-1',
                        min_date_allowed=datetime(datetime.now().year, 1, 1),
                        max_date_allowed=datetime(datetime.now().year, 12, 31),
                        start_date= readings_day['Date'].max(),
                        end_date=readings_day['Date'].max(),
                        display_format='DD-MMM',
                        month_format='MMMM',
                        minimum_nights=0,
                        style={'font-family':'Arial', 'font-size':'11pt'},
                    ),
                ], style={'padding': '10px', 'display': 'flex', 'justify-content': 'space-between'}),
                dcc.Graph(id='Compare-Metric-Past')
                #           figure=get_comparison('2', readings_day['Date'].max().strftime("%Y-%m-%d"), readings_day['Date'].max().strftime("%Y-%m-%d"))),
            ], style={
                    'backgroundColor': 'white',
                    'border': '1px solid darkgray',
                    'box-shadow': '3px 3px 3px rgba(0, 0, 0, 0.2)'
        }),
        # html.Br(),
        # html.Br(),
        # html.Div([
        # html.H2("Correlation", style={'font-family': 'Arial', 'color': 'darkred', 'padding-left': '20px'}),
        #     html.Div([
        #         dcc.DatePickerRange(
        #                 id='date-picker-correlate-1',
        #                 min_date_allowed=readings_day['Date'].min(),
        #                 max_date_allowed=readings_day['Date'].max(),
        #                 start_date=readings_day['Date'].max() - timedelta(days=DAYS_BEFORE_TEMP_1),
        #                 end_date=readings_day['Date'].max(),
        #                 display_format='DD-MMM-YYYY',
        #                 minimum_nights=0,
        #                 style={'font-family':'Arial', 'font-size':'11pt'},
        #             ),
        #         ], style={'padding': '10px', 'display': 'flex', 'justify-content': 'space-between'}),
        #         dcc.Graph(id='Correlate-Metric',
        #                   figure=get_correlation((readings_day["Date"].max() - timedelta(days=DAYS_BEFORE_TEMP_1)).strftime("%Y-%m-%d"),
        #                                           readings_day["Date"].max().strftime("%Y-%m-%d"))),
        #     ], style={
        #             'backgroundColor': 'white',
        #             'border': '1px solid darkgray',
        #             'box-shadow': '3px 3px 3px rgba(0, 0, 0, 0.2)'
        # }),
    ])

if __name__ == '__main__':
    app.run_server(debug=True)

