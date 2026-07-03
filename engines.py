"""
The three engines. Each returns plain dicts; run_daily.py orchestrates
and render.py draws. No engine ever requires user input.
"""

import json
import os
import re
from datetime import date

import anthropic

import config
import prompts

_client = None


def client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        # Key comes from the ANTHROPIC_API_KEY env var (a GitHub Actions
        # secret in production). Never hard-code it.
        _client = anthropic.Anthropic()
    return _client


def _text_of(response) -> str:
    """Join all text blocks. Web-search responses interleave
    server_tool_use / web_search_tool_result blocks with text — we only
    want the text."""
    return "\n".join(
        block.text for block in response.content if block.type == "text"
    )


def _parse_json(raw: str) -> dict:
    """Defensive JSON extraction: strip fences, find the outermost object."""
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in model output:\n{raw[:500]}")
    return json.loads(cleaned[start : end + 1])


# ---------------------------------------------------------------------------
# ENGINE 1 — Market Pulse
# ---------------------------------------------------------------------------

def run_pulse(today: date) -> dict:
    response = client().messages.create(
        model=config.MODEL,
        max_tokens=3000,
        messages=[{
            "role": "user",
            "content": prompts.pulse_prompt(today.strftime("%A, %d %B %Y")),
        }],
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": config.PULSE_MAX_SEARCHES,
            "user_location": {
                "type": "approximate",
                "city": "Mumbai",
                "region": "Maharashtra",
                "country": "IN",
                "timezone": "Asia/Kolkata",
            },
        }],
    )
    data = _parse_json(_text_of(response))
    data.setdefault("items", [])
    data["quiet_day"] = bool(data.get("quiet_day")) or not data["items"]
    return data


# ---------------------------------------------------------------------------
# ENGINE 2 — Sensei Coaching Layer
# ---------------------------------------------------------------------------

def run_coach(today: date) -> dict:
    mode = config.ROTATION[today.toordinal() % len(config.ROTATION)]
    response = client().messages.create(
        model=config.MODEL,
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": (
                MODE_DATE_NOTE.format(d=today.isoformat())
                + prompts.MODE_PROMPTS[mode]
            ),
        }],
    )
    card = _parse_json(_text_of(response))
    card["mode"] = mode
    return card


MODE_DATE_NOTE = "Today's date (variety seed): {d}\n\n"


# ---------------------------------------------------------------------------
# ENGINE 3 — Knowledge bank
# ---------------------------------------------------------------------------

BANK_PATH = os.path.join(os.path.dirname(__file__), "data", "knowledge_bank.json")


def load_bank() -> dict:
    if os.path.exists(BANK_PATH):
        with open(BANK_PATH) as f:
            return json.load(f)
    return {"entities": {}}


def save_bank(bank: dict) -> None:
    with open(BANK_PATH, "w") as f:
        json.dump(bank, f, indent=1, ensure_ascii=False)


def run_bank_merge(pulse: dict, today: date) -> dict:
    """Feed today's items + existing slugs to the model, merge results."""
    bank = load_bank()
    if pulse.get("quiet_day"):
        return bank

    response = client().messages.create(
        model=config.MODEL,
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": prompts.bank_merge_prompt(
                json.dumps(pulse["items"], ensure_ascii=False),
                json.dumps(sorted(bank["entities"].keys())),
            ),
        }],
    )
    updates = _parse_json(_text_of(response))

    for e in updates.get("entries", []):
        slug = e.get("entity_slug", "").strip()
        if not slug:
            continue
        ent = bank["entities"].setdefault(slug, {
            "name": e.get("entity_name", slug),
            "type": e.get("entity_type", "Other"),
            "entries": [],
        })
        ent["entries"].append({
            "date": today.isoformat(),
            "note": e.get("note", ""),
            "deal_type": e.get("deal_type", "Other"),
            "sector": e.get("sector", "Other"),
            "source": e.get("source", ""),
            "url": e.get("url", ""),
        })

    save_bank(bank)
    return bank
