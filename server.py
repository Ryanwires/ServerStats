import json
from pathlib import Path
import socket
import time

from flask import Flask, jsonify, render_template, request
import psutil

app = Flask(__name__)

LAYOUT_PATH = Path(__file__).with_name("layout.json")
DEFAULT_LAYOUT = {
    "canvas": {"width": 122, "height": 250},
    "items": {
        "clock": {"label": "Clock", "x": 90, "y": 0},
        "server_ip": {"label": "Server IP", "x": 90, "y": 35},
        "cpu": {"label": "CPU", "x": 5, "y": 0},
        "temp": {"label": "Temp", "x": 5, "y": 20},
        "disk": {"label": "Disk", "x": 5, "y": 40},
        "uptime_hours": {"label": "Uptime", "x": 5, "y": 60},
        "ram_label": {"label": "RAM Label", "x": 5, "y": 80},
        "ram_bar": {"label": "RAM Bar", "x": 5, "y": 100, "width": 120, "height": 10},
        "offline": {"label": "Offline", "x": 5, "y": 5},
    },
}


def load_layout():
    if not LAYOUT_PATH.exists():
        save_layout(DEFAULT_LAYOUT)
        return DEFAULT_LAYOUT

    try:
        with LAYOUT_PATH.open("r", encoding="utf-8") as layout_file:
            data = json.load(layout_file)
    except (OSError, json.JSONDecodeError):
        save_layout(DEFAULT_LAYOUT)
        return DEFAULT_LAYOUT

    merged = json.loads(json.dumps(DEFAULT_LAYOUT))
    merged["canvas"].update(data.get("canvas", {}))
    for key, value in data.get("items", {}).items():
        if key in merged["items"] and isinstance(value, dict):
            merged["items"][key].update(value)
    return merged


def save_layout(layout):
    with LAYOUT_PATH.open("w", encoding="utf-8") as layout_file:
        json.dump(layout, layout_file, indent=2)
        layout_file.write("\n")


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "No network"
    finally:
        s.close()
    return ip

@app.route('/stats')
def stats():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=0.5),
        "ram_used": round(psutil.virtual_memory().used / (1024**3), 2),
        "ram_total": round(psutil.virtual_memory().total / (1024**3), 2),
        "disk": psutil.disk_usage('/').percent,
        "temp": get_temp(),
        "uptime_hours": round((time.time() - psutil.boot_time()) / 3600, 1),
        "server_ip": get_ip(),
    })

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/layout", methods=["GET", "POST"])
def layout():
    if request.method == "GET":
        return jsonify(load_layout())

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Invalid layout payload"}), 400

    items = payload.get("items")
    if not isinstance(items, dict):
        return jsonify({"error": "Missing items object"}), 400

    current = load_layout()
    for key, value in items.items():
        if key not in current["items"] or not isinstance(value, dict):
            continue

        for field in ("x", "y", "width", "height"):
            if field in value:
                try:
                    current["items"][key][field] = int(value[field])
                except (TypeError, ValueError):
                    return jsonify({"error": f"Invalid {field} for {key}"}), 400

    save_layout(current)
    return jsonify(current)


def get_temp():
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            return temps["coretemp"][0].current
    except:
        pass
    return 0


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
