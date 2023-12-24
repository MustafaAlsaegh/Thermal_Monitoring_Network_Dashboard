tooltipInterval = null;

function initTooltip() {
    const tooltips = Array.from(document.querySelectorAll(".tooltip"));
    const tooltipContainer = document.querySelector(".tooltip-container");
    const tooltipSummaryPane = document.getElementById("tooltip-summary-pane");
    const tooltipPlotPane = document.getElementById("tooltip-plot-pane");

    tooltips.forEach((tooltip) => {
          tooltip.addEventListener("mouseenter", (e) => {
            //if (!tooltipInterval) clearInterval(tooltipInterval);
            tooltipHTML = getTooltip(e.target, tooltipContainer);
            //$(tooltipContainer).html(tooltipHTML);
            // $(tooltipSummaryPane).html(tooltipHTML);
            tooltipContainer.classList.add("fade-in");
            positionTooltip(e);
//            left = `${e.pageX}px`;
//            if (e.pageX + $("#tooltip-container").width() > screen.width) left = (screen.width - 40 - $("#tooltip-container").width()) + "px";
//            tooltipContainer.style.left = left;
//            tooltipContainer.style.top = `${e.pageY}px`;
          }
        );

        tooltip.addEventListener("mouseout", (e) => {
            if (!tooltipInterval) clearInterval(tooltipInterval);
            //tooltipInterval = setInterval(function() { tooltipContainer.classList.remove("fade-in") }, 2000);
            tooltipContainer.classList.remove("fade-in");
          }
        );
    });

    tooltipContainer.addEventListener('mouseenter', () => {
        //if (!tooltipInterval) clearInterval(tooltipInterval);
        tooltipContainer.classList.add("fade-in");
    });

    $(tooltipContainer).click(function(event) {
         event.stopPropagation();
    });

//    tooltipContainer.addEventListener('mouseout', () => {
//        tooltipContainer.classList.remove("fade-in");
//    });
}

function positionTooltip(event) {
    tooltipContainer = document.querySelector(".tooltip-container");
    mouseX = event.clientX;
    mouseY = event.clientY;
    divX = parseInt(mouseX) + window.scrollX - (parseInt(tooltipContainer.offsetWidth) / 2); // Adjust as needed
    divY = (parseInt(mouseY) + window.scrollY - 3 - (parseInt(tooltipContainer.offsetHeight))); // Adjust as needed
    maxX = window.innerWidth - 15 - parseInt(tooltipContainer.offsetWidth);
    maxY = window.innerHeight - parseInt(tooltipContainer.offsetHeight);
    adjustedX = Math.min(divX, maxX);
    adjustedY = Math.min(divY, maxY);
    if (adjustedX < 0) adjustedX = 0;
    if (adjustedY < 0) adjustedY = 0;
    tooltipContainer.style.left = `${adjustedX}px`;
    tooltipContainer.style.top = `${adjustedY}px`;
}

function getTooltip(item, container) {
    var itemType = $(item).attr("RangeType");
    var eventDates = JSON.parse($(item).attr("EventDates"))
    var dateRange = getViewDateRangeByItem(item);
    if (itemType == "TSMonth") {
        plotTimeSeries("tooltip-plot-pane", dateRange[0], dateRange[1], false);
        $("#tooltip-summary-pane").html(getTooltipSummary(itemType, eventDates));
        $("#spnViewMainChart").html(getTooltipViewLink(dateRange[0], dateRange[1]));
    } else if (itemType == "TSDate") {
        plotSpatialView('tooltip-plot-pane', dateRange[0]);
        $("#tooltip-summary-pane").html(getTooltipSummary(itemType, eventDates));
        $("#spnViewMainChart").html("&nbsp;");
    }
}

function getTooltipViewLink(fromDate, toDate) {
    return "<a href = javascript:viewTSOnMainChart('" + formatDate(new Date(fromDate)) + "','" + formatDate(new Date(toDate)) + "')>View on main chart</a>";
}

function getTooltipSummary(itemType, eventDates) {
    var html = new Array()
    ranges = eventDates["ranges"];
    if (ranges.length > 0) html.push("<br/><b>Heat Wave" + ((ranges.length > 1)?"s":"") + "</b>");
    html.push("<ul>")
    for (var t = 0; t < ranges.length; t++) {
        html.push("<li>" + formatDate(new Date(ranges[t]["min"]), "DDMMMYYYY") + " - " + formatDate(new Date(ranges[t]["max"]), "DDMMMYYYY") + "</li>");
    }
    html.push("</ul>")

    if (itemType == "TSDate") {
        if (spacialViewDifferences) {
            row1 = new Array();
            row2 = new Array();
            sensorLocations = Object.keys(spacialViewDifferences);
            for (var i = 0; i < sensorLocations.length; i++) {
                if (sensorLocations[i] == NWS_MONROE_SENSOR_NAME) continue;
                row1.push("<th style = 'font-family:Arial;font-size:10pt;padding:2px;border:1px solid darkgray'>" + sensorLocations[i] + "</th>");
                color  = (parseFloat(spacialViewDifferences[sensorLocations[i]]) < 0.00)?"blue":"red";
                row2.push("<th style = 'font-family:Arial;font-size:10pt;padding:2px;border:1px solid darkgray;color:" + color + "'>" + spacialViewDifferences[sensorLocations[i]].toFixed(2) + "</th>");
            }

            html.push("<b>Temperature Differences compared to NWS - Monroe</b>");
            html.push("<br/><table width = '100%' style = 'border-collapse:collapse;'>");
            html.push("<tr>" + row1 + "</tr>");
            html.push("<tr>" + row2 + "</tr>");
            html.push("</table><br/>");
        }
    }
    return html.join("");
}

function getViewDateRangeByItem(item) {
    viewDateRanges = [];
    var itemType = $(item).attr("RangeType");
    var viewType = $(item).attr("IconType");
    eventDates = JSON.parse($(item).attr("EventDates"))
    minDate = new Date(eventDates["minmax"]["min"]);
    maxDate = new Date(eventDates["minmax"]["max"]);
    if (itemType == "TSMonth") {
        if (viewType == "HeatWave") {
            viewDateRanges.push(minDate); viewDateRanges.push(maxDate);
        } else {
            tickText = $(item).attr("TickText");
            parts = tickText.split(",");
            monthIndex = parseInt(months.indexOf(parts[0].trim())) + 1;
            year = parseInt((2000 + parseInt(parts[1].trim())));
            startDate = new Date(monthIndex + "/1/" + year);
            endDate = new Date(monthIndex + "/1/" + year);
            endDate.setMonth(endDate.getMonth() + 1); endDate.setDate(0);
            viewDateRanges.push(startDate); viewDateRanges.push(endDate);
        }
    } else if (itemType == "TSDate") {
        tickText = $(item).attr("TickText");
        parts = tickText.split("/");
        date = new Date(parts[0].trim() +"/" + parts[1].trim() + "/" + parts[2].trim());
        viewDateRanges.push(date); viewDateRanges.push(date);
    }

    return viewDateRanges;
}

function viewIconClicked(item) {
    var dateRange = getViewDateRangeByItem(item);
    closeTooltip();
    viewTSOnMainChart(formatDate(new Date(dateRange[0])), formatDate(new Date(dateRange[1])), $(item).attr("RangeType") == "TSMonth");
}

function closeTooltip() {
    $("#tooltip-container").removeClass("fade-in");
}

