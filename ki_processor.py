# ki_processor.py
import os
from dotenv import load_dotenv
from data_models import db, Weather, AIAnalysis
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

    text += (
        "Provide a concise summary of the data, insights "
        "and a detailed weather forecast in German."
    )

    return text


def analyze_weather():
    # ✅ App-Context MUSS vom Aufrufer kommen (Route / Task)
    last_entries_raw = get_last_weather(300)

    if not last_entries_raw:
        return "No weather data found in database."

    last_entries = [format_weather_entry(e) for e in last_entries_raw]
    prompt = prepare_prompt(last_entries)

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "You are a weather analysis assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    ai_text = response.choices[0].message.content.strip()

    # ✅ KI-Ergebnis speichern
    analysis = AIAnalysis(
        model="gpt-5-mini",
        prompt=prompt,
        response=ai_text,
        data_points=len(last_entries)
    )

    db.session.add(analysis)
    db.session.commit()

    return ai_text
