"""
All prompts in one place. Engines import from here; edit freely.
Every prompt that expects JSON says so explicitly and forbids preamble
and Markdown fences — parsing still strips fences defensively.
"""

import config


# ---------------------------------------------------------------------------
# ENGINE 1 — Market Pulse
# ---------------------------------------------------------------------------

def pulse_prompt(today_str: str) -> str:
    return f"""Today is {today_str} (India). Search the web for TODAY'S and the
last 24-48 hours' developments, and build a five-section morning brief for
an ECM banker covering Indian BFSI. Sections:

1. "deals" — Indian ECM and M&A deal updates: IPO / QIP / OFS / rights
   filings, launches, pricing, listings, block deals, stake sales; notable
   mandates by {", ".join(config.COMPETITOR_BANKS)}; and anything material
   about these PE firms: {", ".join(config.TARGET_FIRMS)}.
2. "market" — Indian equity market update: index moves and why, FII/DII
   flows, sector rotation, primary-market subscription/listing performance.
3. "macro" — macro that moves Indian capital markets: RBI policy and rates,
   inflation, INR, crude, bond yields, relevant global cues (Fed, US yields).
4. "headlines" — the day's key business headlines beyond the above:
   corporate results, leadership changes, large-cap news an MD would expect
   you to have seen.
5. "regulatory" — actions, circulars, consultations from
   {", ".join(config.REGULATORS)} affecting capital raising or BFSI.

For EACH section select UP TO FIVE items, most significant first.
Significance means: worth knowing before the morning call. Ignore routine
price-target changes and recycled stories. An item belongs in exactly one
section. If a section has genuinely nothing material, return it as an
empty list — do NOT pad with noise.

Respond with ONLY a JSON object, no preamble, no Markdown fences:

{{
  "sections": {{
    "deals":      [ITEM, ...],
    "market":     [ITEM, ...],
    "macro":      [ITEM, ...],
    "headlines":  [ITEM, ...],
    "regulatory": [ITEM, ...]
  }},
  "one_line_read": "a single sentence summarising the day's tone for Indian ECM"
}}

where each ITEM is:
{{
  "headline": "one sharp line, max 15 words",
  "source": "publication name",
  "url": "link if available, else empty string",
  "significance": "one line: why this matters",
  "pitch_angle": "one line: how an ECM banker could act on this, or empty string if none",
  "tags": {{
    "companies": ["Company Name"],
    "deal_type": "IPO | QIP | OFS | M&A | Regulatory | Macro | Market | Other",
    "sector": "e.g. NBFC, Insurance, AMC, Bank, Fintech, Market Infra, or empty"
  }}
}}"""


# Section order + display labels used by the renderer.
SECTION_ORDER = [
    ("deals", "Deals"),
    ("market", "Market"),
    ("macro", "Macro"),
    ("headlines", "Key headlines"),
    ("regulatory", "Regulatory"),
]

# Only durable sections feed the knowledge bank; daily market/macro
# commentary would just be noise in six months.
BANK_SECTIONS = ["deals", "regulatory"]


# ---------------------------------------------------------------------------
# ENGINE 2 — Sensei Coaching Layer (teaches, never quizzes)
# ---------------------------------------------------------------------------

_COACH_PREAMBLE = f"""You write a daily 60-second coaching card for one specific
reader. Context on the reader:

{config.PROFILE}

Rules for every card:
- TEACH, don't test. Pose the question, then immediately give the worked
  answer. The reader should get full value by reading alone, typing nothing.
- Write the answer the way a sharp MD would explain it across a desk — not
  like a textbook. Concrete numbers, real trade-offs, Indian market context.
- Where natural, anchor to the reader's actual deal exposure listed above.
  Never invent facts about those deals beyond what is public.
- Total length: readable in about 60 seconds (~250-350 words).

Respond with ONLY a JSON object, no preamble, no Markdown fences:
{{
  "mode": "<mode name>",
  "title": "short card title",
  "question": "the drill or question, 1-3 sentences",
  "teaching": "the worked answer / model reasoning, in Markdown-free plain prose with paragraph breaks as \\n\\n"
}}"""

MODE_PROMPTS = {
    "technical": _COACH_PREAMBLE + """

Today's mode: "technical".
Pick ONE real ECM or FIG-M&A structuring question of the kind asked in
foreign-IB and PE interviews — e.g. IPO vs QIP sequencing, OFS mechanics,
anchor allocation strategy, insurance embedded-value valuation, NBFC
book-value multiples, holdco discounts, pre-IPO placement pricing tension.
Vary the topic day to day (use today's date as a seed for variety).
Then give the model answer.""",

    "behavioral": _COACH_PREAMBLE + """

Today's mode: "behavioral".
Pick ONE fit/behavioral question this reader is likely to face when
interviewing at a foreign bank or PE fund ("walk me through your best
deal", "why buy-side", "a time you pushed back on a senior", "why should
we hire someone from a domestic franchise"). Then give NOT a script to
memorise but the reasoning pattern behind a strong answer — what the
interviewer is actually probing, the structure of a good response, and
the traps. Show one brief illustrative sketch anchored to his real deal
exposure.""",

    "sensei": _COACH_PREAMBLE + """

Today's mode: "sensei".
Write in the voice of the Philosopher from "The Courage to Be Disliked" —
calm, Socratic, gently provocative, Adlerian. Pose ONE question that cuts
at something plausible in this reader's situation: the pull between
recognition and contribution, separation of tasks amid family expectation,
the courage to be ordinary while chasing an exit, treating the future as
decided. Then give the sensei's own reasoning on it — dialogue-flavoured
prose is fine. Do not lecture; question the premise first. Do NOT claim to
know anything about his specific week — stay at the level of what is
plausibly true of anyone in his position.""",
}


# ---------------------------------------------------------------------------
# ENGINE 3 — Knowledge bank merge
# ---------------------------------------------------------------------------

def bank_merge_prompt(items_json: str, existing_entities_json: str) -> str:
    return f"""You maintain a structured knowledge bank on Indian BFSI capital
markets. Below are (a) today's market pulse items and (b) the current list
of entity slugs already in the bank.

TODAY'S ITEMS:
{items_json}

EXISTING ENTITY SLUGS:
{existing_entities_json}

For each item, produce knowledge-bank entries: which entity (company,
regulator, or PE firm) it belongs to, reusing an existing slug when one
matches, otherwise creating a new slug (lowercase-hyphenated). Write the
note as a durable reference sentence (facts that stay useful in six
months), not news copy.

Respond with ONLY a JSON object, no preamble, no Markdown fences:
{{
  "entries": [
    {{
      "entity_slug": "bajaj-housing-finance",
      "entity_name": "Bajaj Housing Finance",
      "entity_type": "Issuer | Regulator | PE Firm | Bank | Other",
      "note": "durable one-to-two-sentence reference note",
      "deal_type": "IPO | QIP | OFS | M&A | Regulatory | PE | Other",
      "sector": "NBFC | Insurance | AMC | Bank | Fintech | Market Infra | Other",
      "source": "publication",
      "url": ""
    }}
  ]
}}"""
