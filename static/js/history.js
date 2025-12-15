// -----------------------------------------
// Tabelle laden
// -----------------------------------------
async function loadHistory() {
    const res = await fetch("/api/history");
    const data = await res.json();

    const tbody = document.getElementById("history-body");
    tbody.innerHTML = "";  // alte Zeilen entfernen

    data.history.forEach(row => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td style="padding: 8px;">${row.timestamp}</td>
            <td style="padding: 8px;">${row.temperature} °C</td>
            <td style="padding: 8px;">${row.humidity} %</td>
            <td style="padding: 8px;">${row.pressure} hPa</td>
        `;

        tbody.appendChild(tr);
    });
}

// -----------------------------------------
// Live-Werte laden
// -----------------------------------------
async function refreshCurrent() {
    const res = await fetch("/api/current");
    const json = await res.json();

    document.getElementById("temp-value").innerText = json.temperature + " °C";
    document.getElementById("hum-value").innerText = json.humidity + " %";
    document.getElementById("press-value").innerText = json.pressure + " hPa";
}

// -----------------------------------------
// Intervall für Live-Werte → alle 10 Sekunden
// -----------------------------------------
setInterval(refreshCurrent, 10000);

// -----------------------------------------
// Intervall für History-Tabelle → alle 60 Sekunden
// -----------------------------------------
setInterval(loadHistory, 60000);

// -----------------------------------------
// Initiales Laden beim Start
// -----------------------------------------
refreshCurrent();
loadHistory();
