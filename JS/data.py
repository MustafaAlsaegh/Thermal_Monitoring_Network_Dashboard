import pandas as pd
from datetime import datetime
from itertools import combinations

readings_file, nws_file, sensors_file  = "static/data/sensor_readings.csv", "static/data/NWS_Data.csv", "static/data/sensors.csv"
readings, sensors, readings_day, readings_hours, heat_wave_ranges, high_diff_ranges, sensor_locations, sensor_subset = None, None, None, None, None, None, None, None
data_loaded = False
reading_start_date = '01-01-2020'
DAYS_BEFORE_TEMP_1 = 200
DAYS_BEFORE_GEO = 7
HOURLY_DAYS_RANGE = 30
FIVE_MINS_READINGS_RANGE = 15
ROLLING_AVERAGE_WINDOW = 5
HEAT_WAVE_THRESHOLD_DAYS = 2
NWS_MONROE_COUNTY = (39.140999436, -86.6166642)
HEAT_WAVE_MIN_HEAT_INDEX = 80.0
HIGH_READING_DIFF_THRESHOLD = 3.0
HIGH_READING_DIFF_DAYS = 0
NWS_MONROE_SENSOR_NAME = "NWS - Monroe"

monroe_county = dict(lat=39.1690, lon=-86.5200)
heat_index_bands = [dict(type='rect', y0=-20, y1=-10, fillcolor='#05014a', opacity=0.2, name="Extreme Cold: Risk of frostbite and hypothermia. Dangerously cold conditions", layer='below'),
                    dict(type='rect', y0=-10, y1=20, fillcolor='#00008B', opacity=0.2, name="Very Cold: Risk of frostbite. Prolonged exposure may lead to hypothermia", layer='below'),
                    dict(type='rect', y0=20, y1=40, fillcolor='#0000CD', opacity=0.2, name="Cold: Risk of frostbite with prolonged exposure", layer='below'),
                    dict(type='rect', y0=40, y1=60, fillcolor='#ADD8E6', opacity=0.2, name="Cool: Generally comfortable, but dress warmly in cool conditions", layer='below'),
                    dict(type='rect', y0=60, y1=80, fillcolor='#00FF00', opacity=0.2, name="Comfortable: No discomfort expected", layer='below'),
                    dict(type='rect', y0=80, y1=90, fillcolor='#FFFF00', opacity=0.2, name="Caution: Fatigue possible with prolonged exposure and physical activity", layer='below'),
                    dict(type='rect', y0=90, y1=105, fillcolor='#FFA500', opacity=0.2, name="Extreme Caution: Heat cramps and heat exhaustion possible with prolonged exposure and physical activity", layer='below'),
                    dict(type='rect', y0=105, y1=130, fillcolor='#FF0000', opacity=0.2, name="Danger: Heat stroke, heat cramps, and heat exhaustion likely with prolonged exposure and physical activity", layer='below'),
                    dict(type='rect', y0=130, y1=1000, fillcolor='#8b0000', opacity=0.2, name="Extreme Danger: Heat stroke highly likely. Dangerously hot conditions", layer='below'),
                ]


def load(reload = False):
    global readings, sensors, data_loaded, readings_day, readings_hours, heat_wave_ranges, high_diff_ranges, sensor_locations, sensor_subset
    if not data_loaded or reload:
        load_sensor_data()
        nws = read_NWS_data()
        readings_day = pd.concat([readings_day, nws], ignore_index=True)
        nws["Date"] = pd.to_datetime(nws["Date"]).dt.strftime('%Y-%m-%d 11:00:00')
        readings_hours = pd.concat([readings_hours, nws], ignore_index=True)
        readings_hours["Date"] = pd.to_datetime(readings_hours["Date"])
        sensors.loc[len(sensors.index)] = [0, "NWS", NWS_MONROE_SENSOR_NAME, NWS_MONROE_COUNTY[0], NWS_MONROE_COUNTY[1]]
        detect_heat_wave_ranges()
        detect_high_diff_ranges()
        sensor_locations = dict(zip(sensors["Sensor Id"], sensors["Location"]))
        # Get the sensor subset
        sensor_subset = pd.merge(readings.groupby(["Sensor Id"]).agg({"Date": ["min", "max"]}).droplevel(level=[0], axis=1).reset_index().sort_values(by=["max"], ascending=[False]),
                    sensors, on="Sensor Id").drop_duplicates(subset=["Latitude", "Longitude"]).sort_values(by="Location")[["Sensor Id", "Location", "Latitude", "Longitude"]]
        sensor_subset.columns = ["id", "location", "latitude", "longitude"]
        sensor_subset.loc[len(sensor_subset.index)] = [0, NWS_MONROE_SENSOR_NAME, NWS_MONROE_COUNTY[0], NWS_MONROE_COUNTY[1]]
        data_loaded = True
        print("Data Load Completed")


def load_sensor_data():
    global readings, sensors, readings_day, readings_hours
    readings = pd.read_csv(readings_file, header=None, usecols=[1, 2, 3, 4, 6], names=["Date", "Temperature", "Rel Humidity", "Dew Point", "Sensor Id"])
    sensors = pd.read_csv(sensors_file, header=None, usecols=[0, 1, 4, 6, 7], names=["Sensor Id", "Name", "Location", "Latitude", "Longitude"])
    readings["Date"] = pd.to_datetime(readings["Date"])
    readings = drop_outliers(readings, "Temperature")
    readings_day = readings.groupby([readings['Date'].dt.date, readings["Sensor Id"]]).agg({"Temperature": ["mean", "max", "min"], "Rel Humidity": ["mean"],
                            "Dew Point": ["mean"]}).droplevel(axis=1, level=[1]).reset_index()
    readings_day.columns = ["Date", "Sensor Id", "Temperature_mean", "Temperature_max", "Temperature_min", "Rel Humidity_mean", "Dew Point_mean"]
    readings_day["Heat Index_mean"] = readings_day.apply(lambda row: compute_heat_index(row), axis=1)
    readings_day["Date"] = pd.to_datetime(readings_day["Date"])

    readings_day = readings.groupby([readings['Date'].dt.date, readings["Sensor Id"]]).agg({"Temperature": ["mean", "max", "min"], "Rel Humidity": ["mean"],
                    "Dew Point": ["mean"]}).droplevel(axis=1, level=[1]).reset_index()
    readings_day.columns = ["Date", "Sensor Id", "Temperature_mean", "Temperature_max", "Temperature_min", "Rel Humidity_mean", "Dew Point_mean"]
    readings_day["Heat Index_mean"] = readings_day.apply(lambda row: compute_heat_index(row), axis=1)
    readings_day["Date"] = pd.to_datetime(readings_day["Date"])

    readings_hours = readings.copy()
    readings_hours["Date"] = readings_hours["Date"].dt.strftime('%Y-%m-%d %H:00:00')

    readings_hours = readings_hours.groupby([readings_hours['Date'], readings_hours["Sensor Id"]]).agg({"Temperature": ["mean", "max", "min"], "Rel Humidity": ["mean"],
                            "Dew Point": ["mean"]}).droplevel(axis=1, level=[1]).reset_index()
    readings_hours.columns = ["Date", "Sensor Id", "Temperature_mean", "Temperature_max", "Temperature_min", "Rel Humidity_mean", "Dew Point_mean"]
    readings_hours["Heat Index_mean"] = readings_hours.apply(lambda row: compute_heat_index(row), axis=1)
    readings_hours["Date"] = pd.to_datetime(readings_hours["Date"])

    print("Loaded Sensor Data")


def read_NWS_data():
    nws = pd.read_csv(nws_file, usecols=[1, 2, 3, 4, 7, 8, 9])[["datetime", "temp", "tempmax", "tempmin", "humidity", "dew", "feelslike"]]
    nws["Sensor Id"] = 0
    nws.insert(1, 'Sensor Id', nws.pop('Sensor Id'))
    nws.columns = ["Date", "Sensor Id", "Temperature_mean", "Temperature_max", "Temperature_min", "Rel Humidity_mean", "Dew Point_mean", "Heat Index_mean"]
    nws["Date"] = pd.to_datetime(nws["Date"])
    nws = drop_outliers(nws, "Temperature_mean")
    print("Read Nws Data")
    return nws


def drop_outliers(df, column_name):
    mean = df[column_name].mean()
    std = df[column_name].std()
    threshold = 3
    return df[(df[column_name] >= mean - threshold * std) & (df[column_name] <= mean + threshold * std)]


def compute_heat_index(row, type_id = 1):
    temperature, humidity = (row["Temperature_mean"], row["Rel Humidity_mean"]) if type_id == 1 else (row["Temperature_min"], row["Rel Humidity_min"]) if type_id == 2 else (row["Temperature_max"], row["Rel Humidity_max"])
    c = [-42.379, 2.04901523, 10.14333127, -0.22475541, -6.83783e-3,
         -5.481717e-2, 1.22874e-3, 8.5282e-4, -1.99e-6]
    t2 = temperature ** 2
    r2 = humidity ** 2
    heat_index = c[0] + c[1]*temperature + c[2]*humidity + c[3]*temperature*humidity + c[4]*t2 + c[5]*r2 + \
                    c[6]*t2*humidity + c[7]*temperature*r2 + c[8]*t2*r2
    return heat_index


def flatten_readings(metric_name, new_name):
    global readings_day
    sensor_data = readings_day.copy()
    sensor_data = pd.merge(sensor_data, sensors, on = "Sensor Id")[["Date", "Location", metric_name]]
    sensor_data.columns = ["Date", "Location", new_name]
    sensor_locations = sensor_data["Location"].unique()
    new_df = sensor_data.copy()
    for i in range(0, len(sensor_locations)):
        new_df = pd.merge(new_df, sensor_data[sensor_data["Location"] == sensor_locations[i]], on = "Date", how = "outer")
        new_df.rename(columns = {new_df.columns[-1:][0]: sensor_locations[i]}, inplace=True)
        new_df = new_df[list(new_df.columns)[0:(i + 1)] + list(new_df.columns)[-1:]]
    return new_df


def detect_heat_wave_ranges():
    global heat_wave_ranges
    flat_heat_index = flatten_readings("Heat Index_mean", "Heat Index")
    # Calculate the heatwave date ranges. 3 consecutive days above 90 are considered heat wave
    flat_heat_index["Heat Wave"] = (flat_heat_index[NWS_MONROE_SENSOR_NAME] > HEAT_WAVE_MIN_HEAT_INDEX).astype(int)
    flat_heat_index['Group'] = (flat_heat_index['Heat Wave'].ne(flat_heat_index['Heat Wave'].shift()) | flat_heat_index['Heat Wave'].eq(0)).cumsum()
    cum_sum_flat = flat_heat_index[flat_heat_index['Heat Wave'] == 1].groupby(['Group', 'Heat Wave'])['Date'].agg(['min', 'max']).reset_index()
    heat_wave_ranges = cum_sum_flat[cum_sum_flat['max'] - cum_sum_flat['min'] >= pd.to_timedelta(str(HEAT_WAVE_THRESHOLD_DAYS) + ' days')]
    heat_wave_ranges = heat_wave_ranges.sort_values(by=["min", "max"], ascending=[True, True])[["min", "max"]]
    heat_wave_ranges["min"] = pd.to_datetime(heat_wave_ranges["min"]).dt.strftime("%m/%d/%Y")
    heat_wave_ranges["max"] = pd.to_datetime(heat_wave_ranges["max"]).dt.strftime("%m/%d/%Y")
    heat_wave_ranges["MinMonth"] = pd.to_datetime(heat_wave_ranges["min"]).dt.strftime("%Y%m").astype(int)
    heat_wave_ranges["MaxMonth"] = pd.to_datetime(heat_wave_ranges["max"]).dt.strftime("%Y%m").astype(int)
    print("Heat Wave Ranges Detected")


def detect_high_diff_ranges():
    global high_diff_ranges
    flat_temperature = flatten_readings("Temperature_mean", "Temperature")
    flat_temperature['Threshold Exceeded'] = 0
    sensor_combinations = list(combinations(flat_temperature.columns[1:], 2))
    for sensor_pair in sensor_combinations:
        sensor1, sensor2 = sensor_pair
        # Exclude rows where either sensor reading is NaN
        valid_rows = ~flat_temperature[[sensor1, sensor2]].isnull().any(axis=1)
        diff = abs(flat_temperature.loc[valid_rows, sensor1] - flat_temperature.loc[valid_rows, sensor2])
        flat_temperature.loc[valid_rows, 'Threshold Exceeded'] = (flat_temperature.loc[valid_rows, 'Threshold Exceeded'] | (diff > HIGH_READING_DIFF_THRESHOLD)).astype(int)

    flat_temperature['Group'] = (flat_temperature['Threshold Exceeded'].ne(flat_temperature['Threshold Exceeded'].shift()) | flat_temperature['Threshold Exceeded'].eq(0)).cumsum()
    cum_sum_flat = flat_temperature[flat_temperature['Threshold Exceeded'] == 1].groupby(['Group', 'Threshold Exceeded'])['Date'].agg(['min', 'max']).reset_index()
    high_diff_ranges = cum_sum_flat[cum_sum_flat['max'] - cum_sum_flat['min'] >= pd.to_timedelta(str(HIGH_READING_DIFF_DAYS) + ' days')]
    high_diff_ranges = high_diff_ranges.sort_values(by=["min", "max"], ascending=[True, True])[["min", "max"]]
    high_diff_ranges["min"] = pd.to_datetime(high_diff_ranges["min"]).dt.strftime("%m/%d/%Y")
    high_diff_ranges["max"] = pd.to_datetime(high_diff_ranges["max"]).dt.strftime("%m/%d/%Y")
    high_diff_ranges["MinMonth"] = pd.to_datetime(high_diff_ranges["min"]).dt.strftime("%Y%m").astype(int)
    high_diff_ranges["MaxMonth"] = pd.to_datetime(high_diff_ranges["max"]).dt.strftime("%Y%m").astype(int)
    print("High Difference Ranges Detected")


def get_day_readings(start_date, end_date, columns):
    readings_slice = readings_day.loc[(readings_day["Date"].dt.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
                        & (readings_day["Date"].dt.date <= datetime.strptime(end_date, '%Y-%m-%d').date())][columns]
    return readings_slice


def get_hour_readings(start_date, end_date, columns):
    readings_slice = readings_hours.loc[(readings_hours["Date"] >= datetime.strptime(start_date + " 00:00:00", '%Y-%m-%d %H:%M:%S'))
                    & (readings_hours["Date"] <= datetime.strptime(end_date + " 23:59:59", '%Y-%m-%d %H:%M:%S'))]
    return readings_slice


def get_heat_wave_ranges(start_year_month, end_year_month):
    global heat_wave_ranges
    heat_wave_ranges_period = heat_wave_ranges[(heat_wave_ranges["MinMonth"] >= start_year_month) & (heat_wave_ranges["MaxMonth"] <= end_year_month)]
    heat_wave_ranges_period["min"] = pd.to_datetime(heat_wave_ranges_period["min"])
    heat_wave_ranges_period["max"] = pd.to_datetime(heat_wave_ranges_period["max"])
    return heat_wave_ranges_period


def get_high_diff_ranges(start_year_month, end_year_month):
    global high_diff_ranges
    high_diff_ranges_period = high_diff_ranges[(high_diff_ranges["MinMonth"] >= start_year_month) & (high_diff_ranges["MaxMonth"] <= end_year_month)]
    high_diff_ranges_period["min"] = pd.to_datetime(high_diff_ranges_period["min"])
    high_diff_ranges_period["max"] = pd.to_datetime(high_diff_ranges_period["max"])
    return high_diff_ranges_period