import time
import requests
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V4  # change if needed

SERVER = "http://192.168.1.227:5000/stats"

def get():
    try:
        return requests.get(SERVER, timeout=2).json()
    except:
        return None

def draw_bar(draw, x, y, w, h, percent):
    draw.rectangle((x, y, x + w, y + h), outline=0)
    fill = int(w * (percent / 100))
    draw.rectangle((x, y, x + fill, y + h), fill=0)

def render(epd, s):
    image = Image.new("1", (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)

    try:
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_mid = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_big = ImageFont.load_default()
        font_mid = ImageFont.load_default()

    server_ip = s.get("server_ip", "N/A")
#    draw.text((80, 30), server_ip, font=font_mid, fill=0)
    now = time.strftime("%H:%M")

    # --------------------
    # BIG CLOCK (top right)
    # --------------------
    draw.text((90, 0), now, font=font_big, fill=0)

    # --------------------
    # IP under clock
    # --------------------
    draw.text((90, 35), f"{server_ip}", font=font_mid, fill=0)

    # --------------------
    # SERVER DATA (left column)
    # --------------------
    if not s:
        draw.text((5, 5), "OFFLINE", font=font_mid, fill=0)
        epd.displayPartial(epd.getbuffer(image))
        return

    cpu = s.get("cpu", 0)
    temp = s.get("temp", 0)
    disk = s.get("disk", 0)
    uptime = s.get("uptime_hours", 0) 

    draw.text((5, 0), f"CPU {cpu:.1f}%", font=font_mid, fill=0)
    draw.text((5, 20), f"TEMP {temp:.1f}C", font=font_mid, fill=0)
    draw.text((5, 40), f"DISK {disk:.1f}%", font=font_mid, fill=0)
    draw.text((5, 60), f"UP {uptime:.1f}h", font=font_mid, fill=0)

    # --------------------
    # RAM BAR (FULL WIDTH bottom)
    # --------------------
    ram_used = s.get("ram_used", 0)
    ram_total = s.get("ram_total", 1)
    ram_percent = (ram_used / ram_total) * 100

    draw.text((5, 80), f"RAM {ram_used:.1f}/{ram_total:.1f}GB", font=font_mid, fill=0)

    # full width bar
    bar_x, bar_y, bar_w, bar_h = 5, 100, 120, 10
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
