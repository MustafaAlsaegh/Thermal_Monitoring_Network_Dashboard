function formatDate(date, format) {
    if (!format) return date.getFullYear() + "-" + (date.getMonth() + 1) + "-" + date.getDate();
    if (format == "DDMMMYYYY") return  (date.getDate() <= 9? "0"+date.getDate():date.getDate()) + "-" + months[(date.getMonth())] + "-" + date.getFullYear();
}

function getDateFromYYYYMMDDStr(dateStr) {
    parsedDate = null;
    try {
        [datePart, timePart] = dateStr.split(" ");
        [year, month, day] = datePart.split("-");
        [hour, minute, second] = (!timePart)?[0, 0, 0]:timePart.split(":");
        [year, month, day] = [(year)?parseInt(year):1, (month)?parseInt(month):0, (day)?parseInt(day):1];
        [hour, minute, second] = [(hour)?parseInt(hour):0, (minute)?parseInt(minute):0, (second)?parseInt(second):0];
        parsedDate = new Date(year, month - 1, day, hour, minute, second);
    } catch(e){
        parsedDate = new Date(dateStr);
    }
    return parsedDate;
}

function getTemperatureColor(temperature) {
    var hue = (1 - (temperature - MIN_TEMPERATURE) / (MAX_TEMPERATURE - MIN_TEMPERATURE)) * 240;
    var saturation = 100;
    var lightness = 50;
    var rgb = hslToRgb(hue, saturation, lightness);
    var hexColor = rgbToHex(rgb[0], rgb[1], rgb[2]);
    return hexColor;
}

function hslToRgb(h, s, l) {
    h /= 360;
    s /= 100;
    l /= 100;
    var r, g, b;
    if (s === 0) {
        r = g = b = l;
    } else {
        var hue2rgb = function hue2rgb(p, q, t) {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1 / 6) return p + (q - p) * 6 * t;
            if (t < 1 / 2) return q;
            if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
            return p;
        };

        var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        var p = 2 * l - q;

        r = hue2rgb(p, q, h + 1 / 3);
        g = hue2rgb(p, q, h);
        b = hue2rgb(p, q, h - 1 / 3);
    }
    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

function rgbToHex(r, g, b) {
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}


function calculateTickInterval(dateDifference) {
  const thresholds = {
    '3mo': 3 * 30 * 24 * 60 * 60 * 1000, // 3 months
    '1mo': 30 * 24 * 60 * 60 * 1000, // 1 month
    '1w': 7 * 24 * 60 * 60 * 1000, // 1 week
    '1d': 24 * 60 * 60 * 1000, // 1 day
    '12h': 12 * 60 * 60 * 1000, // 12 hours
    '6h': 6 * 60 * 60 * 1000, // 6 hours
    '3h': 3 * 60 * 60 * 1000, // 3 hours
    '1h': 60 * 60 * 1000, // 1 hour
  };

  for (const [interval, threshold] of Object.entries(thresholds)) {
    if (dateDifference > threshold) {
      return threshold;
    }
  }

  //Default
  return thresholds["1h"];
}


function calculateTickVals(startDate, endDate, tickInterval) {
  tickVals = [];
  currentTick = startDate.getTime();
  tickCount = Math.round((endDate.getTime() - startDate.getTime())/24, 0);
  for (var t = 0; t < tickCount; t++) {

  }
  while (currentTick <= endDate.getTime()) {
    tickVals.push(new Date(currentTick));
    currentTick += tickInterval;
  }
  return tickVals;
}


function calculateTickText(startDate, endDate, tickInterval) {
  const tickText = [];
  let currentTick = startDate.getTime();
  while (currentTick <= endDate.getTime()) {
    tickText.push(formatDate(new Date(currentTick), "DDMMMYYYY"));
    currentTick += tickInterval;
  }
  return tickText;
}
