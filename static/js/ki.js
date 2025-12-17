document.getElementById("analyze-btn").addEventListener("click", async () => {
    const resultDiv = document.getElementById("ki-result");

    resultDiv.innerHTML = "⏳ KI analysiert Wetterdaten...";

    try {
        const response = await fetch("/api/analyze");
        const data = await response.json();

        resultDiv.innerHTML = `<h3>KI Analyse & Vorhersage</h3><p>${data.result}</p>`;
    } catch (error) {
        resultDiv.innerHTML = "❌ Fehler bei der KI-Anfrage.";
    }
});
