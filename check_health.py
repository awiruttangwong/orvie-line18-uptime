from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


health = json.loads(Path(sys.argv[1]).read_text())
now = datetime.now(timezone.utc)

assert health.get("status") == "ok", "service status is not ok"
report = health.get("owner_report") or {}
notifier = health.get("owner_report_notifier") or {}

assert report.get("background_alive") is True, "owner report worker is not alive"
assert notifier.get("background_alive") is True, "owner notifier worker is not alive"
assert int(report.get("registered_owner_recipients") or 0) >= 4, "owner recipient registry is incomplete"
assert int(notifier.get("registered_recipients") or 0) >= 4, "notifier owner registry is incomplete"
assert int(report.get("sync_failures") or 0) == 0, "Meta sync has failures"
assert int(health.get("execution_errors") or 0) == 0, "LINE execution errors detected"

last_tick = parse(notifier.get("last_tick_at"))
assert last_tick is not None, "notifier has never ticked"
assert (now - last_tick).total_seconds() <= 180, "notifier tick is stale"

started = parse(health.get("started_at"))
synced = parse(report.get("synced_at"))
if started is None or (now - started).total_seconds() > 12 * 60:
    assert synced is not None, "report sync never completed after startup grace"
    assert (now - synced).total_seconds() <= 15 * 60, "report sync is stale"

print(
    "healthy",
    f"owners={report.get('registered_owner_recipients')}",
    f"conversations={report.get('conversations')}",
    f"synced_at={report.get('synced_at')}",
    f"last_tick_at={notifier.get('last_tick_at')}",
)
