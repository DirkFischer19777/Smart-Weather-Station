// ================================
// Globale Chart-Referenzen
// ================================
let tempChart = null;
let humChart = null;
let pressChart = null;

// ================================
// 24h Wetterdaten laden
// ================================
async function loadWeatherCharts() {
    const res = await fetch("/api/history/24h");
    const data = await res.json();

    if (!data.history || data.history.length === 0) {
        console.warn("No 24h weather data available");
        return;
    }

    const labels = data.history.map(r => r.timestamp);
    const temperatures = data.history.map(r => r.temperature);
    const humidity = data.history.map(r => r.humidity);
    const pressure = data.history.map(r => r.pressure);

    drawTemperatureChart(labels, temperatures);
    drawHumidityChart(labels, humidity);
    drawPressureChart(labels, pressure);
}

// ================================
// Temperatur-Chart (ROT)
// ================================
function drawTemperatureChart(labels, data) {
    const ctx = document.getElementById("tempChart").getContext("2d");

    if (tempChart) tempChart.destroy();

    tempChart = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Temperature (°C)",
                data,
                borderColor: "rgb(220, 53, 69)",       // Rot
                backgroundColor: "rgba(220, 53, 69, 0.1)",
                pointRadius: 2,
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    title: {
                        display: true,
                        text: "°C"
                    }
                },
                x: {
                    ticks: {
                        maxTicksLimit: 12
                    }
                }
            }
        }
    });
}

// ================================
// Luftfeuchtigkeit-Chart (BLAU)
// ================================
function drawHumidityChart(labels, data) {
    const ctx = document.getElementById("humChart").getContext("2d");

    if (humChart) humChart.destroy();

    humChart = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Humidity (%)",
                data,
                borderColor: "rgb(13, 110, 253)",       // Blau
                backgroundColor: "rgba(13, 110, 253, 0.1)",
                pointRadius: 2,
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    title: {
                        display: true,
                        text: "%"
                    }
                },
                x: {
                    ticks: {
                        maxTicksLimit: 12
                    }
                }
            }
        }
    });
}

// ================================
// Luftdruck-Chart (GRÜN)
// ================================
function drawPressureChart(labels, data) {
    const ctx = document.getElementById("pressChart").getContext("2d");

    if (pressChart) pressChart.destroy();

    pressChart = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: "Pressure (hPa)",
                data,
                borderColor: "rgb(25, 135, 84)",        // Grün
                backgroundColor: "rgba(25, 135, 84, 0.1)",
                pointRadius: 2,
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    title: {
                        display: true,
                        text: "hPa"
                    }
                },
                x: {
                    ticks: {
                        maxTicksLimit: 12
                    }
                }
            }
        }
    });
}

// ================================
// Initialisierung & Intervall
// ================================
loadWeatherCharts();
setInterval(loadWeatherCharts, 60000);
