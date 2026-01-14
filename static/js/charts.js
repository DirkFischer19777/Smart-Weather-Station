let weatherChart = null;

async function loadWeatherChart() {
    const res = await fetch("/api/history/24h");
    const data = await res.json();

    if (!data.history || data.history.length === 0) {
        return;
    }

    const labels = data.history.map(r => r.timestamp);
    const temperatures = data.history.map(r => r.temperature);
    const humidity = data.history.map(r => r.humidity);
    const pressure = data.history.map(r => r.pressure);

    const ctx = document.getElementById("weatherChart").getContext("2d");

    if (weatherChart) {
        weatherChart.destroy();
    }

    weatherChart = new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [
                {
                    label: "Temperature (°C)",
                    data: temperatures,
                    tension: 0.3
                },
                {
                    label: "Humidity (%)",
                    data: humidity,
                    tension: 0.3
                },
                {
                    label: "Pressure (hPa)",
                    data: pressure,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: "index",
                intersect: false
            },
            scales: {
                x: {
                    ticks: {
                        maxTicksLimit: 12
                    }
                }
            }
        }
    });
}

loadWeatherChart();
setInterval(loadWeatherChart, 60000);
