import time
import requests
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V4  # change if needed

SERVER = "http://192.168.1.227:5000/stats"
LAYOUT_URL = "http://192.168.1.227:5000/layout"


DEFAULT_LAYOUT = {
    "items": {
        "clock": {"x": 90, "y": 0},
        "server_ip": {"x": 90, "y": 35},
        "cpu": {"x": 5, "y": 0},
        "temp": {"x": 5, "y": 20},
        "disk": {"x": 5, "y": 40},
        "uptime_hours": {"x": 5, "y": 60},
        "ram_label": {"x": 5, "y": 80},
        "ram_bar": {"x": 5, "y": 100, "width": 120, "height": 10},
        "offline": {"x": 5, "y": 5},
    }
}

def get():
    try:
        return requests.get(SERVER, timeout=2).json()
    except:
        return None

def get_layout():
    try:
        remote = requests.get(LAYOUT_URL, timeout=2).json()
        merged = {"items": {}}
        for key, defaults in DEFAULT_LAYOUT["items"].items():
            merged["items"][key] = defaults.copy()
            if isinstance(remote.get("items", {}).get(key), dict):
                merged["items"][key].update(remote["items"][key])
        return merged
    except:
        return DEFAULT_LAYOUT


def render(epd, s):
    image = Image.new("1", (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    layout = get_layout()["items"]

    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_mid = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_big = ImageFont.load_default()
        font_mid = ImageFont.load_default()

    now = time.strftime("%H:%M")

    if not s:
        offline = layout["offline"]
        draw.text((offline["x"], offline["y"]), "OFFLINE", font=font_mid, fill=0)
        epd.displayPartial(epd.getbuffer(image))
        return

    server_ip = s.get("server_ip", "N/A")
    clock = layout["clock"]
    server_ip_text = layout["server_ip"]
    cpu = s.get("cpu", 0)
    temp = s.get("temp", 0)
    disk = s.get("disk", 0)
    uptime = s.get("uptime_hours", 0) 

    draw.text((clock["x"], clock["y"]), now, font=font_big, fill=0)
    draw.text((server_ip_text["x"], server_ip_text["y"]), f"{server_ip}", font=font_mid, fill=0)
    draw.text((layout["cpu"]["x"], layout["cpu"]["y"]), f"CPU {cpu:.1f}%", font=font_mid, fill=0)
    draw.text((layout["temp"]["x"], layout["temp"]["y"]), f"TEMP {temp:.1f}C", font=font_mid, fill=0)
    draw.text((layout["disk"]["x"], layout["disk"]["y"]), f"DISK {disk:.1f}%", font=font_mid, fill=0)
    draw.text((layout["uptime_hours"]["x"], layout["uptime_hours"]["y"]), f"UP {uptime:.1f}h", font=font_mid, fill=0)

    ram_used = s.get("ram_used", 0)
    ram_total = s.get("ram_total", 1)
    ram_percent = (ram_used / ram_total) * 100

    ram_label = layout["ram_label"]
    ram_bar = layout["ram_bar"]
    draw.text((ram_label["x"], ram_label["y"]), f"RAM {ram_used:.1f}/{ram_total:.1f}GB", font=font_mid, fill=0)

    bar_x = ram_bar["x"]
    bar_y = ram_bar["y"]
    bar_w = ram_bar.get("width", 120)
    bar_h = ram_bar.get("height", 10)
    draw.rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), outline=0)
    draw.rectangle((bar_x, bar_y, bar_x + int(bar_w * ram_percent / 100), bar_y + bar_h), fill=0)

    epd.displayPartial(epd.getbuffer(image))

def main():
    epd = epd2in13_V4.EPD()
    epd.init()

    # 🧼 FULL REFRESH ON STARTUP
    epd.Clear(0xFF)

    while True:
        render(epd, get())
        time.sleep(2)  # safer than 1s for e-ink lifespan

if __name__ == "__main__":
    main()
