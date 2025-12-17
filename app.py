from flask import Flask, render_template
import requests
import time
from data_models import db, start_background_collector
import os

app = Flask(__name__)

# ------------------- DATABASE CONFIG -------------------
# Ensure /data folder exists
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Database file path (absolute path prevents SQLite errors)
db_path = os.path.join(DATA_DIR, "weather.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Tabellen einmalig erzeugen
with app.app_context():
    db.create_all()


# ------------------- PICO DATA FETCHING -------------------
PICO_URL = "http://192.168.178.115/"

def get_pico_data(retries=3, timeout=5):
    """Try fetching JSON from the Pico. Return dict with temperature, humidity, pressure."""
    headers = {"Connection": "close", "Accept": "application/json, text/plain"}

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(PICO_URL, headers=headers, timeout=timeout)
            resp.raise_for_status()

            # Try normal JSON parse
            try:
                data = resp.json()
            except ValueError:
                # fallback: try extract JSON from HTML or plain text
                text = resp.text
                app.logger.debug("Pico returned non-JSON response: %s", text[:200])

                import re
                m = re.search(r'\{.*"temperature".*\}', text, flags=re.S)
                if m:
                    import json
                    try:
                        data = json.loads(m.group(0))
                    except Exception:
                        data = {}
                else:
                    data = {}

            return {
                "temperature": try_float(data.get("temperature")),
                "humidity": try_float(data.get("humidity")),
                "pressure": try_float(data.get("pressure")),
                "error": None
            }

        except Exception as e:
            app.logger.warning("Attempt %d: Error fetching data from Pico: %s", attempt, e)
            last_error = e
            time.sleep(0.3)

    # Rückgabe bei Fehlern
    return {
        "temperature": None,
        "humidity": None,
        "pressure": None,
        "error": str(last_error)
    }


def try_float(x):
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


# ------------------- ROUTES -------------------
@app.route("/")
def index():
    sensor_data = get_pico_data()
    return render_template("index.html", data=sensor_data)


@app.route("/api/history")
def api_history():
    from data_models import Weather

    rows = Weather.query.order_by(Weather.id.desc()).limit(10).all()

    # umkehren, damit älteste oben stehen
    rows = list(reversed(rows))

    return {
        "history": [
            {
                "timestamp": row.timestamp.strftime("%H:%M:%S"),
                "temperature": row.temperature,
                "humidity": row.humidity,
                "pressure": row.pressure,
            }
            for row in rows
        ]
    }


@app.route("/api/current")
def api_current():
    data = get_pico_data()
    return {
        "temperature": data["temperature"],
        "humidity": data["humidity"],
        "pressure": data["pressure"]
    }

@app.route("/api/analyze")
def api_analyze():
    from ki_processor import analyze_weather

    try:
        result = analyze_weather()
        return {"result": result}
    except Exception as e:
        return {"result": f"Fehler bei der KI-Analyse: {e}"}


# ------------------- MAIN ENTRY -------------------
if __name__ == "__main__":
    # Nur starten, wenn NICHT im Debug-ReLoader
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_background_collector(app, get_pico_data, interval=300)

    # Starte lokalen Server
    app.run(host="127.0.0.1", port=5001, debug=True)
