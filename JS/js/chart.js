function mapReadingsDataTypes() {
    ALL_SENSORS = Object.keys(sensorReadings);
    for (var i = 0; i < ALL_SENSORS.length; i++) {
        TS1_SELECTED_SENSORS.push(ALL_SENSORS[i]);
        readings = sensorReadings[ALL_SENSORS[i]];
        readings["Date"] = readings["Date"].map(dateStr => getDateFromYYYYMMDDStr(dateStr));
        readings["Readings"] = readings["Readings"].map(floatStr => parseFloat(floatStr));
    }
}

function plotTimeSeries(elementId, startDate, endDate, showLegend) {
    sensorLocations = Object.keys(sensorReadings)
    chartData = []
    maxY = 0;
    minX = new Date("01/01/3000");
    maxX = new Date("01/01/1900");

    startDate = (startDate == null)?getDateFromYYYYMMDDStr(DEFAULT_START):startDate;
    endDate = (endDate == null)?getDateFromYYYYMMDDStr(DEFAULT_END):endDate;

    startDate = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate(), 0, 0, 0);
    endDate = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate(), 23, 59, 59);
    if (currentInterval == "DAY") {
        startDate.setDate(startDate.getDate() - 1);
        endDate.setDate(endDate.getDate() + 1);
    }

    for (var i = 0; i < sensorLocations.length; i++) {
        if (TS1_SELECTED_SENSORS != null) {
            if (TS1_SELECTED_SENSORS.indexOf(sensorLocations[i]) == -1) continue;
        }
        readings = sensorReadings[sensorLocations[i]];
        filteredReadings = filterReadings(readings, startDate, endDate);
        maxY = Math.max(maxY, ...filteredReadings["Readings"]);
        minX = Math.min(minX, ...filteredReadings["Date"]);
        maxX = Math.max(maxX, ...filteredReadings["Date"]);
        var trace = {
          type: "scatter",
          mode: "lines",
          name: sensorLocations[i],
          x: filteredReadings["Date"],
          y: filteredReadings["Readings"],
          line: {color: 'viridis', width: 2.5},
        }
        if (sensorLocations[i] == NWS_MONROE_SENSOR_NAME) trace["line"]["dash"] = "dashdot";
        chartData.push(trace);
    }

//    var tickInterval = calculateTickInterval(new Date(maxX).getTime() - new Date(minX).getTime());
//    console.log("Tick Interval :" + tickInterval);
//    tick0 = formatDate(new Date(minX)) + " 00:00:00";
    heatWaveZones = getHeatWaveZonesInRange(startDate, endDate);
    threshold = 80;

//    console.log(calculateTickVals(new Date(minX), new Date(maxX), tickInterval));
//    console.log(calculateTickText(new Date(minX), new Date(maxX), tickInterval));

    var layout = {
      title: $("#selMetric").val().substring(0, ($("#selMetric").val().length - 5)),
      yaxis: { autorange: true },
      xaxis: {
        visible: true,
        type:"date",
//        tick0: tick0,
//        dtick: tickInterval,
//        tickvals: calculateTickVals(new Date(minX), new Date(maxX), tickInterval),
//        ticktext: calculateTickText(new Date(minX), new Date(maxX), tickInterval)
      },
      showlegend: showLegend,
      legend: { "orientation":"h"},
      shapes: [],
      annotations: []
    };

    heatWaveZonesInRange = getHeatWaveZonesInRange(startDate, endDate);
    if (heatWaveZonesInRange.length > 0) {
        heatWaveZonesInRange.forEach(({ start, end }) => {
            start = (startDate.getTime() >= start.getTime())?startDate:start;
            end = (end.getTime() >= endDate.getTime())?endDate:end;
//            start = (new Date(start).getTime() < startDate.getTime())?:start;
//            end = (new Date(end).getTime() > endDate.getTime())?endDate:end;
            layout.shapes.push({
                type: 'rect',
//                xref: 'x',
//                yref: 'paper',
                x0: start,
                x1: end,
                y0: HEAT_WAVE_MIN_HEAT_INDEX,
                y1: maxY,
                fillcolor: 'yellow',
                opacity: 0.4,
                layer: 'below',
                line: { width: 0 },
            });

            layout.annotations.push({
                x: start,
                y: HEAT_WAVE_MIN_HEAT_INDEX + 6,
                text: "Heat Wave",
                showarrow: true,
                font: {color: 'red'},
            });
        });
    }

    Plotly.newPlot(elementId, chartData, layout);
}


function plotTimeSeries2(elementId, startDate, endDate, showLegend) {
    sensorLocations = Object.keys(multiReadings["DAY"]);
    chartData = []
    maxY = 0;

    if (startDate != null) {
        startDate = new Date(startDate);
        startDate.setDate(startDate.getDate() - 2);
    }

    if (endDate != null) {
        endDate = new Date(endDate);
        endDate.setDate(endDate.getDate() + 2);
    }

    for (var i = 0; i < sensorLocations.length; i++) {
        readings1 = multiReadings["DAY"][sensorLocations[i]];
        filteredReadings = filterReadings(readings1, startDate, endDate);
        maxY = Math.max(maxY, ...filteredReadings["Readings"]);
        var trace = {
          type: "scatter",
          mode: "lines",
          name: sensorLocations[i],
          x: filteredReadings["Date"],
          y: filteredReadings["Readings"],
          line: {color: 'viridis', width: 2.5},
        }
        if (sensorLocations[i] == NWS_MONROE_SENSOR_NAME) trace["line"]["dash"] = "dashdot";
        chartData.push(trace);

        readings2 = multiReadings["HOUR"][sensorLocations[i]];
        filteredReadings = filterReadings(readings2, startDate, endDate);
        maxY = Math.max(maxY, ...filteredReadings["Readings"]);
        var trace = {
          type: "scatter",
          mode: "lines",
          name: sensorLocations[i],
          x: filteredReadings["Date"],
          y: filteredReadings["Readings"],
          line: {color: 'viridis', width: 2.5},
        }
        if (sensorLocations[i] == NWS_MONROE_SENSOR_NAME) trace["line"]["dash"] = "dashdot";
        chartData.push(trace);
    }

    heatWaveZones = getHeatWaveZonesInRange(startDate, endDate);
    threshold = 85;

    var layout = {
      title: $("#selMetric").val().substring(0, ($("#selMetric").val().length - 5)),
      yaxis: { autorange: true },
      xaxis: { visible: true, type:"date",},
      showlegend: showLegend,
      legend: { "orientation":"h"},
      shapes: [],
      annotations: []
    };

    if (heatWaveZones.length > 0) {
        heatWaveZones.forEach(({ start, end }) => {
            layout.shapes.push({
                type: 'rect',
                //xref: 'x',
                //yref: 'paper',
                x0: start,
                x1: end,
                y0: HEAT_WAVE_MIN_HEAT_INDEX,
                y1: maxY,
                fillcolor: 'yellow',
                opacity: 0.4,
                layer: 'below',
                line: { width: 0 },
            });

            // You can also add annotations if needed
            layout.annotations.push({
                x: start,
                y: threshold + 5, // Adjust the y position of the annotation
                text: "Heat Wave",
                showarrow: true,
                font: {color: 'red'}, // Customize the font color
            });
        });
    }

    Plotly.newPlot(elementId, chartData, layout);
}

function plotSpatialView(elementId, startDate) {
    sensorGeoLoc = {"Location": [], "Reading": [], "Latitude": [], "Longitude": [], "Text": []};
    dateStr = formatDate(startDate, "DDMMMYYYY");
    for (var t = 0; t < sensorGeoData["Location"].length; t++) {
        sensorMetric = sensorReadings[sensorGeoData["Location"][t]];
        if (sensorMetric && sensorMetric["Date"] && sensorMetric["Date"].length > 0) {
            index = sensorMetric["Date"].findIndex(date => date.getTime() === startDate.getTime());
            if (index != -1) {
                sensorGeoLoc["Location"].push(sensorGeoData["Location"][t]);
                sensorGeoLoc["Reading"].push(sensorMetric["Readings"][index]);
                sensorGeoLoc["Latitude"].push(sensorGeoData["Latitude"][t]);
                sensorGeoLoc["Longitude"].push(sensorGeoData["Longitude"][t]);
                sensorGeoLoc["Text"].push("<b>" + dateStr + "<br><b>" + sensorGeoData["Location"][t] + " : <b>" + parseFloat(sensorMetric["Readings"][index]).toFixed(2));
            }
        }
    }

    nwsIndex = sensorGeoLoc["Location"].findIndex(location => location == NWS_MONROE_SENSOR_NAME);
    spacialViewDifferences = {};
    if (nwsIndex != -1) {
        for (var t = 0; t < sensorGeoLoc["Location"].length; t++) {
            spacialViewDifferences[sensorGeoLoc["Location"][t]] = parseFloat(sensorGeoLoc["Reading"][nwsIndex]) - parseFloat(sensorGeoLoc["Reading"][t]);
        }
    }

    data = [{
      type: 'scattermapbox',
      lat: sensorGeoLoc["Latitude"],
      lon: sensorGeoLoc["Longitude"],
      text: sensorGeoLoc["Location"], //sensorGeoLoc["Text"],
      mode: 'markers',
      //showlegend:false,
      marker: {
        size: 14,
        color: sensorGeoLoc["Reading"],
        colorscale: 'Viridis',
        colorbar:null,
//        colorbar: {
//            title: currentMetric
//        },
//          colorbar: {
//              title: 'Temperature',
//              tickvals: [/* specify tick values */],
//              ticktext: [/* specify tick labels */],
//              tickmode: 'array',
//              tickangle: -45,
//              len: 0.8,
//              x: 0.1,
//              y: -0.2,
//              xanchor: 'left',
//              yanchor: 'bottom'
//          }
      },
    }];

    // Layout configuration
    const layout = {
      autosize: true,
      hovermode: 'closest',
      mapbox: {
        style: 'open-street-map',
        height:750,
        center: {"lat":39.1600, "lon":-86.5400},
        zoom:12.0
      },
      annotations: [
                {
                      x: sensorGeoLoc["Longitude"][1],
                      y: sensorGeoLoc["Latitude"][1],
                      xref: 'x',
                      yref: 'y',
                      text: 'Biology Building',
                      showarrow: true,
                      arrowhead: 4,
                      ax: 0,
                      ay: -40
                }
      ],
      margin: { t: 0, b: 0, l: 0, r: 0 },
    };

    Plotly.newPlot(elementId, data, layout);
}

function plotBox(elementId, startDate, endDate, showLegend) {
    sensorLocations = Object.keys(sensorReadings)
    chartData = []
    for (var i = 0; i < sensorLocations.length; i++) {
        readings = sensorReadings[sensorLocations[i]];
        filteredReadings = filterReadings(readings, startDate, endDate);
        var trace = {
          y: filteredReadings["Readings"],
          type: "box",
          //boxpoints: 'all',
          jitter: 0.3,
          //pointpos: -1.8,
          name: sensorLocations[i],
        }
        chartData.push(trace);
    }

    var layout = {
      title: 'Box Plot',
      yaxis: { title: 'Values' }
    };

    Plotly.newPlot(elementId, chartData, layout);
}

function filterReadings(readings, startDate, endDate) {
    filteredReadings = {"Date": [], "Readings": []};
    if (startDate == null && endDate == null) return readings;

    if (startDate == null) startDate = new Date("01/01/1990");
    if (endDate == null) endDate = new Date("01/01/2999");

    for (var i = 0; i < readings["Date"].length; i++) {
        date = readings["Date"][i].getTime();
        reading = readings["Readings"][i];
        if (date >= startDate && date <= endDate) {
            filteredReadings["Date"].push(date);
            filteredReadings["Readings"].push(reading);
        }
    }
    return filteredReadings;
}

function getHeatWaveZonesInRange(startDate, endDate) {
    //if (currentMetric != "Heat Index_mean") return [];
    startDate = (startDate == null)?getDateFromYYYYMMDDStr(DEFAULT_START):new Date(startDate);
    endDate = (endDate == null)?getDateFromYYYYMMDDStr(DEFAULT_END):new Date(endDate);
    startDate.setHours(0); startDate.setMinutes(0); startDate.setSeconds(0);
    endDate.setHours(23); endDate.setMinutes(59); endDate.setSeconds(59);
    startDate = startDate.getTime();
    endDate = endDate.getTime();
    minDates = heatWavePeriods["MinDate"];
    maxDates = heatWavePeriods["MaxDate"];
    heatWaveZones = [];
    for (var j = 0; j < minDates.length; j++) {
        if (startDate <= new Date(maxDates[j]).getTime() && endDate >= new Date(minDates[j]).getTime()) {
            heatWaveZones.push({start: new Date(minDates[j]), end: new Date(maxDates[j])});
        }
    }
    return heatWaveZones;
}

function getBestStartRange(plotStart, plotEnd) {
    bestRange = {};
    heatWaveZones = getHeatWaveZonesInRange(plotStart, plotEnd);
    startDate = null; endDate = null;
    if (heatWaveZones.length > 0) {
        [startDate, endDate] = [heatWaveZones[heatWaveZones.length - 1]["start"], heatWaveZones[heatWaveZones.length - 1]["end"]];
    } else {
        startDate = (plotStart == null)?getDateFromYYYYMMDDStr(DEFAULT_START):new Date(plotStart);
        endDate = (plotEnd == null)?getDateFromYYYYMMDDStr(DEFAULT_END):new Date(plotEnd);
        bestRange = {start: startDate, end: endDate};
    }

    newStart = new Date(endDate);
    if (currentInterval == "DAY") {
        newStart.setDate(newStart.getDate() - 10);
    }

    newStart.setHours(0); newStart.setMinutes(0); newStart.setSeconds(0);
    endDate.setHours(23); endDate.setMinutes(59); endDate.setSeconds(59);
    return {start: newStart, end: endDate};
}

function getSensorsWithHighDiff(startDate, endDate, selectedSensors) {
    for (var t = 0; t < selectedSensors.length; t++) {
        readings = sensorReadings[selectedSensors[i]];
        filteredReadings = filterReadings(readings, startDate, endDate);
        var zeroArray = [...new Array(filteredReadings["Readings"].length)].map(() => 0);
        distance = Math.sqrt(filteredReadings["Readings"].reduce((sum, val, index) => sum + Math.pow(val - zeroArray[index], 2), 0));
        console.log();
    }
}