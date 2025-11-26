# data_models.py
import os
import threading
import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import requests

# SQLAlchemy-Instanz – wird später in app.py init_app() aufgerufen
db = SQLAlchemy()


# -----------------------------
# DATABASE MODEL
# -----------------------------
class Weather(db.Model):
    __tablename__ = "weather"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)

    def __repr__(self):
        return f"<Weather {self.timestamp} T={self.temperature} H={self.humidity} P={self.pressure}>"


# -----------------------------
# STORE DATA FUNCTION
# -----------------------------
def store_sensor_data(data: dict):
    """Speichert Sensor-Daten in der Datenbank."""
    entry = Weather(
        temperature=data.get("temperature"),
        humidity=data.get("humidity"),
        pressure=data.get("pressure")
    )
    db.session.add(entry)
    db.session.commit()


# -----------------------------
# BACKGROUND WORKER
# -----------------------------
def start_background_collector(app, fetch_func, interval=10):
    """
    Startet einen Hintergrund-Thread, der alle X Sekunden Daten abholt
    und in SQLite speichert.

    :param app: Flask-App
    :param fetch_func: Funktion, die Sensor-Daten zurückgibt (deine get_pico_data)
    :param interval: Sekunden zwischen Abfragen
    """

    def worker():
        with app.app_context():
            print("[DATA WORKER] Started, saving every", interval, "seconds")

            while True:
                try:
                    data = fetch_func()

                    if data and not data.get("error"):
                        store_sensor_data(data)
                        print("[DATA WORKER] Saved data:", data)
                    else:
                        print("[DATA WORKER] Error:", data.get("error"))

                except Exception as e:
                    print("[DATA WORKER] Exception:", e)

                time.sleep(interval)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
