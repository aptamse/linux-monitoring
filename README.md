# System Health Monitor Script

## Overview

This Python script monitors basic system health metrics and sends email alerts when issues are detected. It checks:

* Disk usage
* System load average
* Availability of specified TCP ports/services

When a threshold is exceeded or a monitored port goes down, the script sends an **alert email**. When the issue is resolved, it sends a **recovery email**.

The script maintains a **state file** so it does not send repeated alerts for the same issue unless the condition changes.

---

## Features

* Disk usage monitoring
* System load monitoring
* TCP port/service availability checks
* Email alert notifications
* Recovery notifications when issues are resolved
* State tracking to prevent duplicate alerts
* Lightweight and cron-friendly

---

## Requirements

* Python **3.6+**
* Network access to SMTP server
* Linux system (uses `os.getloadavg()`)

Required Python modules (built-in):

* `os`
* `json`
* `socket`
* `smtplib`
* `shutil`
* `datetime`
* `email`

No external packages are required.

---

## Configuration

Update the configuration section in the script before running.

### Threshold Settings

```
THRESHOLDS = {
    "disk": 90,
    "load": 10.0
}
```

| Parameter | Description                            |
| --------- | -------------------------------------- |
| disk      | Disk usage percentage threshold        |
| load      | 1-minute system load average threshold |

---

### Port Monitoring

```
PORTS_TO_MONITOR = [
    {"name": "Service1", "host": "127.0.0.1", "port": 22},
    {"name": "Service2", "host": "127.0.0.1", "port": 80}
]
```

You can add any service you want to monitor.

Example:

```
{"name": "MySQL", "host": "127.0.0.1", "port": 3306}
{"name": "Redis", "host": "127.0.0.1", "port": 6379}
```

---

### State File

```
STATE_FILE = "/tmp/system_health_state.json"
```

This file stores the current alert state to avoid sending duplicate notifications.

---

### Email Configuration

```
SMTP_SERVER = "smtp.google.com"
SMTP_PORT = 587
SMTP_USER = "username"
SMTP_PASS = "password"
FROM_EMAIL = "mail@google.com"
TO_EMAILS = ["recipient@google.com"]
```

| Parameter   | Description              |
| ----------- | ------------------------ |
| SMTP_SERVER | SMTP mail server         |
| SMTP_PORT   | SMTP port                |
| SMTP_USER   | SMTP username            |
| SMTP_PASS   | SMTP password            |
| FROM_EMAIL  | Sender email address     |
| TO_EMAILS   | List of recipient emails |

---

## How It Works

1. The script collects system metrics:

   * Disk usage
   * Load average
   * Service ports status

2. It compares values against defined thresholds.

3. If an issue is detected:

   * An **alert email** is sent.

4. When the issue is resolved:

   * A **recovery email** is sent.

5. The script updates the **state file** to track current alert conditions.

---

## Running the Script

Make the script executable:

```
chmod +x system_health_monitor.py
```

Run manually:

```
python3 system_health_monitor.py
```

---

## Running with Cron (Recommended)

Run the script every **5 minutes**:

```
crontab -e
```

Add:

```
*/5 * * * * /usr/bin/python3 /path/system_health_monitor.py >> /var/log/system_health_monitor.log 2>&1
```

This will:

* Execute every 5 minutes
* Save logs to `/var/log/system_health_monitor.log`

---

## Example Alert Email

Subject:

```
⚠️ ALERT: Server Issue Detected
```

Body:

```
Disk usage is HIGH: 95.3% (> 90%)
Port DOWN: Service2 (127.0.0.1:80)
```

---

## Example Recovery Email

Subject:

```
✅ RESOLVED: Server Restored
```

Body:

```
Disk usage recovered: 60.1% (< 90%)
Port UP: Service2 (127.0.0.1:80)
```

---

## File Structure Example

```
/opt/scripts/
    system_health_monitor.py

/tmp/
    system_health_state.json

/var/log/
    system_health_monitor.log
```

---

## Security Recommendations

* Store SMTP credentials securely.
* Restrict script permissions.
* Use environment variables or secrets manager for passwords in production.

---

## Possible Improvements

* Memory usage monitoring
* Multiple disk mount monitoring
* Slack / Teams alerts
* TLS SMTP support
* Service restart automation
* Integration with monitoring tools

---

## License

Internal / Custom Use.
