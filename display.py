from flask import Flask, jsonify
import psutil
import time

app = Flask(__name__)

boot_time = time.time() - psutil.boot_time()

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

def get_temp():
    try:
        temps = psutil.sensors_temperatures()
        if "coretemp" in temps:
            return temps["coretemp"][0].current
    except:
        pass
    return 0

import socket

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
app.run(host='0.0.0.0', port=5000)
