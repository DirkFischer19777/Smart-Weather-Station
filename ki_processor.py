# ki_processor.py
import os
from dotenv import load_dotenv
from datetime import datetime
from data_models import db, Weather
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

# Client initialisieren
client = OpenAI(api_key=API_KEY)


def get_last_weather(n=300):
    """Fetch last n weather entries."""
    return Weather.query.order_by(Weather.timestamp.desc()).limit(n).all()


def format_weather_entry(entry):
    """Convert SQLAlchemy object -> dict."""
    return {
        "timestamp": entry.timestamp.strftime("%H:%M:%S"),
        "temperature": entry.temperature,
        "humidity": entry.humidity,
        "pressure": entry.pressure
    }


def prepare_prompt(entries):
    """Create prompt with weather list."""
    if not entries:
        return "No weather data available."

    text = "Analyze the following weather data:\n"
    for e in entries:
        text += (
            f"Time: {e['timestamp']}, Temp: {e['temperature']}°C, "
            f"Humidity: {e['humidity']}%, Pressure: {e['pressure']} hPa\n"
        )
    text += "Provide a concise summary of data, insights and a detailed weather forecast in German. "

    return text


def analyze_weather():
    print("[DEBUG] Loading last 10 entries...")

    last_entries_raw = get_last_weather(300)
    print("[DEBUG] Raw DB entries:", last_entries_raw)

    last_entries = [format_weather_entry(e) for e in last_entries_raw]
    print("[DEBUG] Formatted entries:", last_entries)

    if not last_entries:
        return "No weather data found in database."

    prompt = prepare_prompt(last_entries)
    print("[DEBUG] Prompt sent to KI:\n", prompt)

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a weather analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        # max_completion_tokens=150
    )

    print("[DEBUG] Raw API response:", response)

    return response.choices[0].message.content.strip()
