function monthRangeChanged(e, data) {
    startDate = data.values.min;
    endDate = data.values.max;
    startDate.setHours(0); startDate.setMinutes(0); startDate.setSeconds(0);
    endDate.setHours(23); endDate.setMinutes(59); endDate.setSeconds(59);
    updateDateRangeSlider(startDate, endDate, startDate, endDate, true);
}

function updateMonthRangeSlider(startDate, endDate) {
    monthRangerStartDate = getDateFromYYYYMMDDStr(startDate);
    monthRangerEndDate = getDateFromYYYYMMDDStr(endDate);
    dateRangerStartDate = getDateFromYYYYMMDDStr(startDate);
    dateRangerEndDate = getDateFromYYYYMMDDStr(endDate);
    monthRangerStartDate.setDate(1);
    if (monthRangerEndDate.getDate() != 31) {
        monthRangerEndDate.setMonth(monthRangerEndDate.getMonth() + 1);
        monthRangerEndDate.setDate(0);
    }
    $("#monthSlider").dateRangeSlider("values", monthRangerStartDate, monthRangerEndDate);
    updateDateRangeSlider(monthRangerStartDate, monthRangerEndDate, dateRangerStartDate, dateRangerEndDate, false);
}

function updateDateRangeSlider(startDate, endDate, selectionStartDate, selectionEndDate, doPlot) {
    newEndDate = new Date(endDate.getTime()); //newEndDate.setHours(0); newEndDate.setMinutes(0); newEndDate.setSeconds(0);
    var daysDiff = Math.ceil((newEndDate.getTime() - startDate.getTime()) / (1000 * 3600 * 24));
    if (daysDiff <= 65) {
        $("#dateSlider").css('visibility', 'visible');
        $("#spnShortRangeText").css('visibility', 'hidden');
        $("#dateSlider").dateRangeSlider("bounds", startDate, newEndDate);
        $("#dateSlider").dateRangeSlider("values", selectionStartDate, selectionEndDate);
        if (doPlot) {
            plotTimeSeries("time-series-chart-1", selectionStartDate, selectionEndDate, true);
        }
        addSliderTable("dateSlider", "dateRangeDataTable", "TSDate", function(text) { return getHeatWaveEventsDateRange(text); });
        $("#dateRangeDataTable").css('visibility', 'visible');
    } else {
        $("#dateSlider").css('visibility', 'hidden');
        $("#dateRangeDataTable").css('visibility', 'hidden');
        $("#spnShortRangeText").css('visibility', 'visible');
        plotTimeSeries("time-series-chart-1", startDate, endDate, true);
    }
}

function setDateRangeSliderValues(date1, date2) {
    date1 = new Date(date1);
    date2 = new Date(date2);
    date1.setHours(0); date1.setMinutes(0); date1.setSeconds(0);
    date2.setHours(23); date2.setMinutes(59); date2.setSeconds(59);
    $("#dateSlider").dateRangeSlider("values", date1, date2);
}

function dateRangeChanged(e, data) {
    plotTimeSeries("time-series-chart-1", data.values.min, data.values.max);
}

function timeSeriesDateChanged(selectedDates) {
    if (selectedDates.length < 2) return;
    fetchTimeSeries(formatDate(new Date(selectedDates[0])), formatDate(new Date(selectedDates[1])));
}

function checkDateRangeSelected() {
    selectedDates = datePickerTimeSeries.selectedDates;
    if (selectedDates.length < 2) {
        alert("Please select a date range");
        return false;
    }

    return true;
}

function metricChanged(metric) {
    if (!checkDateRangeSelected()) return false;
    fetchTimeSeries(formatDate(new Date(selectedDates[0])), formatDate(new Date(selectedDates[1])), metric, $("#selInterval").val());
}

function intervalChanged(interval) {
    if (!checkDateRangeSelected()) return false;
    fetchTimeSeries(formatDate(new Date(selectedDates[0])), formatDate(new Date(selectedDates[1])), $("#selMetric").val(), interval);
}

function viewTSOnMainChart(startDate, endDate, doUpdateSliderRanges) {
    closeTooltip();
    plotTimeSeries("time-series-chart-1", getDateFromYYYYMMDDStr(startDate), getDateFromYYYYMMDDStr(endDate), true);
    if (doUpdateSliderRanges) updateMonthRangeSlider(startDate, endDate);
    else setDateRangeSliderValues(getDateFromYYYYMMDDStr(startDate), getDateFromYYYYMMDDStr(endDate))
}

