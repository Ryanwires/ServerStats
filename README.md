# ServerStats

`ServerStats` is a small server-monitor display project built around:

- a Flask web app that serves live system stats and a layout editor
- a Waveshare e-paper display client that fetches those stats and renders them

The web UI lets you move text around and change text size. The display process reads that saved layout and uses it on the Waveshare screen.

## Files

Main files in this project:

- `server.py`: Flask app with `/stats`, `/layout`, and the web editor
- `Display.py`: Waveshare display renderer
- `layout.json`: saved positions and font sizes
- `templates/index.html`: web UI
- `static/app.js`: web editor logic
- `static/styles.css`: web editor styles
- `fonts/`: bundled DejaVu fonts used by the display renderer

## Install

Clone the repo:

```bash
git clone https://github.com/Ryanwires/ServerStats.git
cd ServerStats
```

Install Python packages:

```bash
pip3 install -r requirements.txt
```

If you are using Debian or Raspberry Pi OS, also install the DejaVu system fonts so Pillow can render scalable text cleanly:

```bash
sudo apt-get update
sudo apt-get install -y fonts-dejavu-core
```

## Run Manually

Start the web server:

```bash
cd ~/ServerStats
python3 server.py
```

Open the editor in a browser:

```text
http://<server-ip>:5000/
```

Start the Waveshare display process:

```bash
cd ~/ServerStats
python3 Display.py
```

## Web UI

The web UI lets you:

- drag text to move it
- type exact `X` and `Y` positions
- change text size
- save the layout back into `layout.json`

The preview also uses live values from `/stats`, so it should stay closer to what the real screen is showing.

## Startup on Boot

If you want the web server and display process to start automatically after reboot, use `systemd`.

### 1. Web Server Service

Create:

```bash
sudo nano /etc/systemd/system/serverstats-web.service
```

Paste:

```ini
[Unit]
Description=ServerStats Web UI
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ryan
WorkingDirectory=/home/ryan/ServerStats
ExecStart=/usr/bin/python3 /home/ryan/ServerStats/server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 2. Display Service

Create:

```bash
sudo nano /etc/systemd/system/serverstats-display.service
```

Paste:

```ini
[Unit]
Description=ServerStats Waveshare Display
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ryan
WorkingDirectory=/home/ryan/ServerStats
ExecStart=/usr/bin/python3 /home/ryan/ServerStats/Display.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. Enable and Start

Reload `systemd`, enable both services, and start them:

```bash
sudo systemctl daemon-reload
sudo systemctl enable serverstats-web.service
sudo systemctl enable serverstats-display.service
sudo systemctl start serverstats-web.service
sudo systemctl start serverstats-display.service
```

### 4. Check Status

```bash
systemctl status serverstats-web.service
systemctl status serverstats-display.service
```

### 5. View Logs

```bash
journalctl -u serverstats-web.service -f
journalctl -u serverstats-display.service -f
```

## Updating

Pull the latest code:

```bash
cd ~/ServerStats
git pull
pip3 install -r requirements.txt
```

Then restart the services:

```bash
sudo systemctl restart serverstats-web.service
sudo systemctl restart serverstats-display.service
```

## Notes

- The web server normally runs on port `5000`.
- `Display.py` currently points at:

```python
SERVER = "http://192.168.1.227:5000/stats"
LAYOUT_URL = "http://192.168.1.227:5000/layout"
```

If your server IP changes, update those values in `Display.py`.

- If text size on the e-paper display does not change, make sure:
  - the new `layout.json` was saved from the web UI
  - `Display.py` was restarted
  - DejaVu fonts are installed

## Typical Setup

Common setup for this project:

1. `server.local` runs `server.py`
2. `02w.local` runs `Display.py`
3. The browser opens `http://server.local:5000/`
4. The display process fetches stats and layout from `server.local`
