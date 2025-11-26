from flask import Flask, render_template
import requests
import time

app = Flask(__name__)

# URL of your Raspberry Pi Pico W webserver
PICO_URL = "http://192.168.178.115/"

def get_pico_data(retries=3, timeout=5):
    """Try fetching JSON from the Pico. Return dict with keys temperature, humidity, pressure or None values on error."""
    headers = {"Connection": "close", "Accept": "application/json, text/plain"}
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(PICO_URL, headers=headers, timeout=timeout)
            resp.raise_for_status()

            # Try to parse JSON first. If Pico returns plain HTML, try to extract numbers defensively.
            try:
                data = resp.json()
            except ValueError:
                # fallback: look at plain text and try to parse numbers (useful for debugging)
                text = resp.text
                app.logger.debug("Pico returned non-JSON response: %s", text[:200])
                # If the Pico returns JSON-like string inside HTML, try to find it:
                import re
                m = re.search(r'\{.*"temperature".*\}', text, flags=re.S)
                if m:
                    try:
                        import json
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

    # after retries, return error info
    return {"temperature": None, "humidity": None, "pressure": None, "error": str(last_error)}

def try_float(x):
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None

@app.route("/")
def index():
    sensor_data = get_pico_data()
    return render_template("index.html", data=sensor_data)

if __name__ == "__main__":
    # Run on 0.0.0.0 if you want to access this from other devices; default 127.0.0.1 is fine for local dev.
    app.run(host="127.0.0.1", port=5001, debug=True)
