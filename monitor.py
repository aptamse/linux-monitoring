#!/usr/bin/env python3
import os
import smtplib
import json
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import shutil
from datetime import datetime


# ===================== CONFIG =====================
THRESHOLDS = {
    "disk": 90,       # %
    "load": 10.0       # 1-minute load avg
}

PORTS_TO_MONITOR = [
    {"name": "Service1", "host": "127.0.0.1", "port": 22},
    {"name": "Service2", "host": "127.0.0.1", "port": 80}
]

STATE_FILE = "/tmp/system_health_state.json"

SMTP_SERVER = "smtp.google.com"
SMTP_PORT = 587
SMTP_USER = "username"
SMTP_PASS = "password"
FROM_EMAIL = "mail@google.com"
TO_EMAILS = ["recepient@google.com"]

# ==================================================

def get_disk_usage():
    total, used, free = shutil.disk_usage("/")
    percent_used = (used / total) * 100
    return round(percent_used, 2)

def get_load_average():
    return os.getloadavg()[0]

def check_port(host, port, timeout=10):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def send_email(subject, message):
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = ", ".join(TO_EMAILS)
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [INFO] Email sent: {subject}")
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [ERROR] Failed to send email: {e}")

def load_state():
    default_state = {
        "disk_alert": False,
        "load_alert": False,
        "port_alerts": {}
    }

    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
            # Ensure all expected keys exist
            for key in default_state:
                if key not in state:
                    state[key] = default_state[key]
            return state
        except Exception as e:
            print(f"[ERROR] Failed to load state file: {e}")
            return default_state
    return default_state

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def main():
    disk_usage = get_disk_usage()
    load_avg = get_load_average()
    state = load_state()

    alert_msgs = []
    recovery_msgs = []

    # -------- Disk Check --------
    if disk_usage > THRESHOLDS["disk"]:
        if not state["disk_alert"]:
            alert_msgs.append(f"Disk usage is HIGH: {disk_usage}% (> {THRESHOLDS['disk']}%)")
            state["disk_alert"] = True
    else:
        if state["disk_alert"]:
            recovery_msgs.append(f"Disk usage recovered: {disk_usage}% (< {THRESHOLDS['disk']}%)")
            state["disk_alert"] = False

    # -------- Load Check --------
    if load_avg > THRESHOLDS["load"]:
        if not state["load_alert"]:
            alert_msgs.append(f"System Load is HIGH: {load_avg} (> {THRESHOLDS['load']})")
            state["load_alert"] = True
    else:
        if state["load_alert"]:
            recovery_msgs.append(f"System Load recovered: {load_avg} (< {THRESHOLDS['load']})")
            state["load_alert"] = False

    # -------- Port Check --------
    for port_info in PORTS_TO_MONITOR:
        name = port_info["name"]
        host = port_info["host"]
        port = port_info["port"]
        key = f"{host}:{port}"

        is_up = check_port(host, port)
        was_alerting = state["port_alerts"].get(key, False)

        if not is_up and not was_alerting:
            alert_msgs.append(f"Port DOWN: {name} ({host}:{port})")
            state["port_alerts"][key] = True
        elif is_up and was_alerting:
            recovery_msgs.append(f"Port UP: {name} ({host}:{port})")
            state["port_alerts"][key] = False

    # -------- Send Alerts --------
    if alert_msgs:
        send_email("⚠️ ALERT: Server Issue Detected", "\n".join(alert_msgs))
    if recovery_msgs:
        send_email("✅ RESOLVED: Server Restored", "\n".join(recovery_msgs))

    save_state(state)

if __name__ == "__main__":
    main()
