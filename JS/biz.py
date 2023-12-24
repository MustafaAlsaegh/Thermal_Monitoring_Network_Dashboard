import numpy as np
import pandas as pd
import json
import data


def init():
    data.load()


def serialize_df(obj):
    if isinstance(obj, pd.DataFrame):
        return obj.to_json(orient='records')
    return obj


def get_readings(start_date, end_date, start_year_month, end_year_month, metric, interval):
    readings = None
    if interval == "DAY": readings = data.get_day_readings(start_date, end_date, ["Date", "Sensor Id", metric])
    elif interval == "HOUR": readings = data.get_hour_readings(start_date, end_date, ["Date", "Sensor Id", metric])
    unique_sensor_ids = list(np.sort(readings["Sensor Id"].unique()))
    heat_wave_ranges_period = data.get_heat_wave_ranges(start_year_month, end_year_month)
    high_diff_ranges_period = data.get_high_diff_ranges(start_year_month, end_year_month)
    sensor_readings = {"Data": {}, "Heat Wave Periods": {}, "High Diff Periods": {}, "Sensor Geo Data": {}}
    for sensor_id in unique_sensor_ids:
        filtered_df = readings[readings["Sensor Id"] == sensor_id]
        filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
        sensor_readings["Data"][data.sensor_locations[sensor_id]] = {"Date": list(filtered_df["Date"].dt.strftime('%Y-%m-%d %H:00:00')), "Readings": list(filtered_df[metric])}
    sensor_readings["Heat Wave Periods"] = {"MinMonth": list(heat_wave_ranges_period["MinMonth"]), "MaxMonth": list(heat_wave_ranges_period["MaxMonth"]), "MinDate": list(heat_wave_ranges_period["min"].dt.strftime('%Y-%m-%d')), "MaxDate": list(heat_wave_ranges_period["max"].dt.strftime('%Y-%m-%d'))}
    sensor_readings["Sensor Geo Data"] = {"Id":list(data.sensor_subset["id"]), "Location":list(data.sensor_subset["location"]), "Latitude":list(data.sensor_subset["latitude"]), "Longitude":list(data.sensor_subset["longitude"])}
    # sensor_readings["High Diff Periods"] = {"MinMonth": list(high_diff_ranges_period["MinMonth"]), "MaxMonth": list(high_diff_ranges_period["MaxMonth"]), "MinDate": list(high_diff_ranges_period["min"].dt.strftime('%Y-%m-%d')), "MaxDate": list(high_diff_ranges_period["max"].dt.strftime('%Y-%m-%d'))}
    sensor_data = json.dumps(sensor_readings)
    return sensor_data

