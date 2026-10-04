"""Sustain inbound checks between delayed GitHub scheduled runs."""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import urlopen

URL = "https://orvie-line18-render.onrender.com/health"
BKK = timezone(timedelta(hours=7))

def active_window(now: datetime) -> bool:
    minute = now.astimezone(BKK).hour * 60 + now.astimezone(BKK).minute
    return minute >= 5 * 60 + 40 or minute < 2 * 60

def check_once() -> bool:
    with tempfile.TemporaryDirectory(prefix="line18-health-") as directory:
        path = Path(directory) / "health.json"
        for attempt in range(3):
            try:
                with urlopen(URL, timeout=100) as response:
                    health = json.load(response)
                path.write_text(json.dumps(health), encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(Path(__file__).with_name("check_health.py")), str(path)],
                    capture_output=True, text=True, timeout=15,
                )
                print(result.stdout.strip() or result.stderr.strip(), flush=True)
                if result.returncode == 0:
                    return True
            except Exception as exc:
                print("health attempt failed:", type(exc).__name__, flush=True)
            if attempt < 2:
                time.sleep(20)
    return False

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=33)
    parser.add_argument("--interval", type=float, default=600)
    args = parser.parse_args()
    if not 1 <= args.cycles <= 33 or args.interval < 0:
        parser.error("cycles must be 1..33 and interval nonnegative")
    failures = 0
    for cycle in range(args.cycles):
        deadline = time.monotonic() + args.interval
        now = datetime.now(BKK)
        print("cycle", cycle + 1, now.isoformat(), flush=True)
        if active_window(now):
            if not check_once():
                failures += 1
                print("cycle unhealthy; continue checking next cycle", flush=True)
        else:
            print("rest window; no Render request", flush=True)
        if cycle + 1 < args.cycles:
            time.sleep(max(0, deadline - time.monotonic()))
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
