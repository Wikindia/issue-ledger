"""
Central configuration. This is the only file you should need to edit
to tune the system. Everything else reads from here.
"""

# Model used for all engines. Sonnet is the right cost/quality point for
# a daily job; switch to an Opus model string if you want heavier reasoning.
MODEL = "claude-haiku-4-5"

# Max web searches the daily pulse call may perform.
PULSE_MAX_SEARCHES = 5

# Timezone label used on the rendered page (cron itself is set in the
# GitHub Actions workflow, in UTC).
TZ_LABEL = "IST"

# ---------------------------------------------------------------------------
# Profile context injected into Engine 2 (coaching) prompts.
# Written in third person on purpose — it is a briefing to the model,
# not a claim the model should parrot back.
# ---------------------------------------------------------------------------
PROFILE = """
The reader is a Chartered Accountant with ~4 years of front-office ECM
experience at an Indian investment bank (SBI Capital Markets), focused on
BFSI. Live deal exposure includes: Bajaj Housing Finance IPO, Tata Capital
IPO, NSE IPO (co-manager), NSDL IPO, Canara HSBC Life IPO, and the
Svatantra Microfin sell-side advisory. He is preparing a move to a foreign
investment bank or a PE / growth-equity fund. He is under real time
pressure: a target exit window in 2026, alongside family expectations and
an arranged-marriage timeline running in parallel.
""".strip()

# Firms tracked for competitor activity in Engine 1.
COMPETITOR_BANKS = [
    "Kotak Investment Banking", "JM Financial", "Axis Capital",
    "ICICI Securities", "IIFL Capital", "Motilal Oswal", "Jefferies India",
    "Citi India", "Morgan Stanley India", "Goldman Sachs India", "Investec",
]

# PE / IB firms in the target list — Engine 3 keeps a standing dossier on each.
TARGET_FIRMS = [
    "True North", "ChrysCapital", "Multiples Alternate Asset Management",
    "Kedaara Capital", "WestBridge Capital", "JM Financial Private Equity",
]

# Regulators watched by Engine 1.
REGULATORS = ["SEBI", "RBI", "IRDAI", "PFRDA"]

# Engine 2 rotation. Day index = date.toordinal() % len(ROTATION).
ROTATION = ["technical", "behavioral", "sensei"]
