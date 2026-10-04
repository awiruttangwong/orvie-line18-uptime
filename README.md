# ORVIE LINE 18 Uptime Watchdog

External watchdog for the public LINE 18 Render service.

- Sends an inbound health request every 10 minutes.
- Verifies the owner-report sync worker and owner notifier worker are alive.
- Exists outside the Render process, so it still runs when Render has spun down.
- A weekly repository heartbeat keeps the public scheduled workflow from becoming inactive.

Target: https://orvie-line18-render.onrender.com/health

This repository intentionally contains no LINE, Meta, Render, or customer secrets.
