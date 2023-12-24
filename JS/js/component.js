function createDateRangeSlider(startDate, endDate) {
    $("#dateSlider").attr("tickCount", "0");
    $("#dateSlider").dateRangeSlider({
      bounds: {min: startDate, max: endDate},
      defaultValues: {min: startDate, max: endDate},
      formatter:function(val) {
          val = new Date(val);
          var day = (val.getDate() <= 9)?"0"+val.getDate():val.getDate();
          var month = months[val.getMonth()];
          var year = val.getFullYear();
          return day + "-" + month + "-" + year;
      },
      scales: [{
          first: function(value){ return value; },
          end: function(value) { return value; },
          next: function(value){
            var next = new Date(value);
            nextTick = new Date(next.setDate(value.getDate() + 1));
            $("#dateSlider").attr("tickCount", parseInt($("#dateSlider").attr("tickCount")) + 1);
            return nextTick;
          },
          label: function(value) {
            var day = (value.getDate() <= 9)?"0"+value.getDate():value.getDate();
            return "" + (parseInt(value.getMonth()) + 1) + "/" + parseInt(value.getDate()) + " /" +  (""+ parseInt(value.getYear())).substring(1, 3);
          },
          format: function(tickContainer, tickStart, tickEnd){
            tickContainer.addClass("myTickClass");
          }
      }]
    });

    $("#dateSlider").bind("userValuesChanged", dateRangeChanged);
}

function createMonthRangeSlider(minDate, maxDate) {
    $("#monthSlider").attr("tickCount", "0");
    $("#monthSlider").dateRangeSlider({
      bounds: {min: minDate, max: maxDate},
      defaultValues: {min: minDate, max: maxDate},
      formatter:function(val) {
          val = new Date(val);
          var month = months[val.getMonth()];
          var year = val.getFullYear();
          return month + "-" + year;
      },
      scales: [{
          first: function(value){ return value; },
          end: function(value) { return value; },
          next: function(value){
            var nextVal = new Date(value);
            var newnextVal = new Date(value);
            nextTick = new Date(nextVal.setMonth(value.getMonth() + 1));
            $("#monthSlider").attr("tickCount", parseInt($("#monthSlider").attr("tickCount")) + 1);
            return nextTick;
          },
          label: function(value){
            //return (value.getMonth() + 1) + "/" + value.getDate() + "/" +  (""+value.getYear()).substring(1, 3);
            return months[value.getMonth()] + ", " + (""+value.getYear()).substring(1, 3);
          },
          format: function(tickContainer, tickStart, tickEnd){
            tickContainer.addClass("myTickClass");
          }
      }]
    });
    $("#monthSlider").bind("userValuesChanged", monthRangeChanged);
    addSliderTable("monthSlider", "monthRangeDataTable", "TSMonth", function(text) { return getHeatWaveEventsMonthRange(text) });
}

function addSliderTable(sliderId, tableDiv, itemType, heatWaveIndicatorFunction) {
    tickItems = $("#" + sliderId).find(".myTickClass");
    var tableHTML = new Array();
    tableHTML.push("<table width = '100%' style = 'padding:0px; border-collapse:collapse;'>");
    for (var j = 0; j < 1; j++) {
     tableHTML.push("<tr>");
      for (var i = 0; i < tickItems.length; i++) {
        eventDates = heatWaveIndicatorFunction($(tickItems[i]).text());
        tableHTML.push("<td style = 'text-align:center;padding-top:10px;padding-bottom:10px;border:1px solid black;width:" + tickItems[i].style.width + ";font-family:Arial;font-size:10px;background-color:" + (eventDates["ranges"].length > 0?"yellow":"white") + "'>" + ((eventDates["ranges"].length > 0 && itemType == "TSMonth")?"<span class = 'tooltip' style = 'cursor:pointer' RangeType = '" + itemType + "' IconType = 'HeatWave' EventDates = '" + JSON.stringify(eventDates) + "' onclick = 'viewIconClicked(this)'><i class='fa-solid fa-temperature-arrow-up' style = 'font-size:10pt;color:red;padding-left:10px;padding-right:10px;'></i></span>":"&nbsp;"));
        tableHTML.push("<span class = 'tooltip' style = 'cursor:pointer;color:blue;' RangeType = '" + itemType + "' IconType = 'View' EventDates = " + JSON.stringify(eventDates) + " TickText = '" + $(tickItems[i]).text() + "' onclick = 'viewIconClicked(this)'><i class='fa-solid fa-eye' style = 'font-size:10pt;'></i></span></td>")
      }
    }
    tableHTML.push("</tr>");
    tableHTML.push("</table>");
    $("#" + tableDiv).html(tableHTML.join(""));
    initTooltip();
}

function getHeatWaveEventsMonthRange(month) {
    return getEventsRangeMonth(month, heatWavePeriods);
}

function getHeatWaveEventsDateRange(date) {
    return getEventsRangeDate(date, heatWavePeriods);
}

function getEventsRangeMonth(month, eventPeriods) {
    parts = month.split(",");
    monthIndex = parseInt(months.indexOf(parts[0].trim())) + 1;
    yearMonth = parseInt((2000 + parseInt(parts[1].trim())) + "" + (monthIndex <= 9? "0"+monthIndex:monthIndex));
    minMonths = eventPeriods["MinMonth"];
    maxMonths = eventPeriods["MaxMonth"];
    minDates = eventPeriods["MinDate"];
    maxDates = eventPeriods["MaxDate"];
    minMax = [];
    eventDates = {"ranges":[], "minmax":{}};
    eventMinMonths = [];
    eventMaxMonths = [];
    count = 0;
    for (var j = 0; j < minMonths.length; j++) {
        if (yearMonth >= parseInt(minMonths[j]) && yearMonth <= parseInt(maxMonths[j])) {
            eventDates["ranges"].push({"min":minDates[j], "max":maxDates[j]});
            minMax.push(getDateFromYYYYMMDDStr(minDates[j]).getTime());
            minMax.push(getDateFromYYYYMMDDStr(maxDates[j]).getTime());
        }
    }
    if (eventDates["ranges"].length > 0) {
        eventDates["minmax"]["min"] = Math.min(...minMax)
        eventDates["minmax"]["max"] = Math.max(...minMax)
    }
    return eventDates;
}

function getEventsRangeDate(date, eventPeriods) {
    parts = date.split("/");
    tickDate = new Date(parseInt(parts[0].trim())+"/"+parseInt(parts[1].trim())+"/"+parseInt(parts[2].trim()));
    tickDate.setHours(0); tickDate.setMinutes(0); tickDate.setSeconds(0);
    tickDate = tickDate.getTime();
    minDates = eventPeriods["MinDate"];
    maxDates = eventPeriods["MaxDate"];
    minMax = [];
    eventDates = {"ranges":[], "minmax":{}};
    eventMinDates = [];
    eventMaxDates = [];
    for (var j = 0; j < minDates.length; j++) {
        if (tickDate >= new Date(minDates[j]).getTime() && tickDate <= new Date(maxDates[j]).getTime()) {
            eventDates["ranges"].push({"min":new Date(minDates[j]).getTime(), "max":new Date(maxDates[j]).getTime()});
            minMax.push(new Date(minDates[j]).getTime());
            minMax.push(new Date(maxDates[j]).getTime());
        }
    }
    if (eventDates["ranges"].length > 0) {
        eventDates["minmax"]["min"] = Math.min(...minMax)
        eventDates["minmax"]["max"] = Math.max(...minMax)
    }
    return eventDates;
}

function createDateRangePicker(componentId, defaultDates) {
    component = flatpickr(componentId, {
        mode: "range",
        dateFormat: "Y-m-d",
        defaultDate: defaultDates,
        onChange: function(selectedDates, dateStr, instance) {
            timeSeriesDateChanged(selectedDates);
        }
    });

    return component;
}
