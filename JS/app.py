from flask import Flask, redirect, url_for, render_template, request, session, jsonify
import json
import decimal
import biz
from datetime import datetime
import calendar

app = Flask(__name__)

with app.app_context():
    biz.init()


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal): return float(obj)


def get_parameter(param_name, type = 'str', defaultValue = None):
    value = request.values.get(param_name)
    value = defaultValue if value is None else value
    return value


@app.route("/")
def home():
    return render_template("HSNWDashboard.html")


def get_date_range(start_date, end_date):
    start_year, start_month = int(datetime.strptime(start_date, "%Y-%m-%d").strftime('%Y')), int(datetime.strptime(start_date, "%Y-%m-%d").strftime('%m'))
    start_date = str(start_year) + "-" + str(start_month) + "-1"
    start_year_month = int(str(start_year) + ("0" + str(start_month) if start_month <= 9 else str(start_month)))
    end_year, end_month = int(datetime.strptime(end_date, "%Y-%m-%d").strftime('%Y')), int(datetime.strptime(end_date, "%Y-%m-%d").strftime('%m'))
    end_date = str(end_year) + "-" + str(end_month) + "-" + str(calendar.monthrange(end_year, end_month)[1])
    end_year_month = int(str(end_year) + ("0" + str(end_month) if end_month <= 9 else str(end_month)))
    return start_date, end_date, start_year_month, end_year_month


@app.route("/gettimeseries", methods = ['POST', 'GET'])
def get_time_series():
    start_date = get_parameter("start_date")
    end_date = get_parameter("end_date")
    metric = get_parameter("metric", defaultValue="Temperature_mean")
    interval = get_parameter("interval", defaultValue="DAY")
    start_date, end_date, start_year_month, end_year_month = get_date_range(start_date, end_date)
    return biz.get_readings(start_date, end_date, start_year_month, end_year_month, metric, interval)


if __name__ == '__main__':
    app.run()