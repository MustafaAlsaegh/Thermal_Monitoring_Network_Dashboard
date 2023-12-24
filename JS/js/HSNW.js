fetching = false;
multiReadings = {};
sensorReadings = null;
heatWavePeriods = null;
sensorGeoData = null;
START_DAYS = -30;
DEFAULT_START = "2023-01-01";
DEFAULT_END = "2023-11-01";
DEFAULT_METRIC = "Temperature_mean";
DEFAULT_INTERVAL = "HOUR";
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
datePickerTimeSeries = null;
currentMetric = null;
currentInterval = null;
spacialViewDifferences = null;
HEAT_WAVE_MIN_HEAT_INDEX = 80.0;
MONROE_COUNTY = {"lat":39.1690, "lon":-86.5200};
NWS_MONROE_SENSOR_NAME = "NWS - Monroe";
TS1_SELECTED_SENSORS = [];
ALL_SENSORS = null;

function fetchData(url, input, successCallback, errorCallback) {
    if (fetching) return;
    fetching = true;
    $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        data: input,
        success: successCallback,
        error: errorCallback
    });
}

function initPage() {
    datePickerTimeSeries = createDateRangePicker("#date-range-picker", [DEFAULT_START, DEFAULT_END]);
    $("#selMetric").val(DEFAULT_METRIC);
    $("#selInterval").val(DEFAULT_INTERVAL);
    fetchTimeSeries(DEFAULT_START, DEFAULT_END, $("#selMetric").val(), $("#selInterval").val());
}

function fetchTimeSeries(startDate, endDate, metric, interval) {
    currentMetric = metric;
    currentInterval = interval;
    fetchData("/gettimeseries", {"start_date": startDate, "end_date": endDate, "metric": metric, "interval":interval}, timeSeriesDataFetched, timeSeriesDataFetchFailed);
}

function timeSeriesDataFetched(data) {
    fetching = false;
    sensorReadings = data["Data"];
    heatWavePeriods = data["Heat Wave Periods"];
    sensorGeoData = data["Sensor Geo Data"];
    mapReadingsDataTypes();
    bestRange = getBestStartRange(null, null);
    plotTimeSeries("time-series-chart-1", null, null, true);
    plotBox("box-plot-chart-1", null, null, true);
    var fig = document.getElementById("time-series-chart-1");
    range = fig.layout.xaxis.range;
    start = getDateFromYYYYMMDDStr(range[0]); start.setHours(0); start.setMinutes(0); start.setSeconds(0);
    end = getDateFromYYYYMMDDStr(range[1]); end.setHours(0); end.setMinutes(0); end.setSeconds(0);
    dateRangeStart = new Date(range[1]); dateRangeStart.setMonth(end.getMonth() - 2);
    createMonthRangeSlider(start, end);
    createDateRangeSlider(dateRangeStart, end);
    initTooltip();
    $("#monthSlider").dateRangeSlider("values", start, end);
    $(document).ready(function() {
        $(document).click(function(event) {
            $("#tooltip-container").removeClass("fade-in");
        });
    });

    //viewTSOnMainChart(bestRange["start"], bestRange["end"], true);
}

function timeSeriesDataFetchFailed(data) {
    alert("Failed Fetching Time Series Data");
    fetching = false;
}



