"""
Daily orchestrator. Run by GitHub Actions on a schedule; can also be run
locally with ANTHROPIC_API_KEY set:

    ANTHROPIC_API_KEY=sk-... python run_daily.py

Order matters: pulse → coach → bank merge → render. Each engine is
isolated so one failure degrades gracefully instead of killing the page.
"""

import json
import os
import sys
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

import engines
import render

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE = os.path.join(HERE, "data", "archive")


def main() -> int:
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    failures = []

    # Engine 1 — Market pulse
    try:
        pulse = engines.run_pulse(today)
    except Exception:
        traceback.print_exc()
        failures.append("pulse")
        pulse = {"items": [], "quiet_day": True,
                 "one_line_read": "Pulse unavailable today — the engine hit an error; yesterday's knowledge bank is unaffected."}

    # Engine 2 — Coaching card
    try:
        card = engines.run_coach(today)
    except Exception:
        traceback.print_exc()
        failures.append("coach")
        card = {"mode": "sensei", "title": "No card today",
                "question": "The coaching engine hit an error.",
                "teaching": "It will return tomorrow. A missed day is information, not a broken chain."}

    # Engine 3 — Knowledge bank merge (skipped automatically on quiet days)
    try:
        bank = engines.run_bank_merge(pulse, today)
    except Exception:
        traceback.print_exc()
        failures.append("bank")
        bank = engines.load_bank()

    # Archive the raw day (public market data only — no personal content)
    os.makedirs(ARCHIVE, exist_ok=True)
    with open(os.path.join(ARCHIVE, f"{today.isoformat()}.json"), "w") as f:
        json.dump({"pulse": pulse, "card": card}, f, indent=1, ensure_ascii=False)

    # Render
    render.render_index(today, pulse, card)
    render.render_bank(today, bank)

    print(f"Done. Failures: {failures or 'none'}")
    # Exit 0 even on partial failure so the site still deploys; the page
    # itself surfaces the failure honestly.
    return 0


if __name__ == "__main__":
    sys.exit(main())
