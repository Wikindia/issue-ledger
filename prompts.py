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
last 24-48 hours' most significant developments in Indian equity capital
markets, specifically:

1. IPO / QIP / OFS / rights-issue filings, launches, pricing, listings
2. M&A and stake sales in Indian BFSI (banks, NBFCs, insurers, AMCs,
   fintech, market infrastructure)
3. Regulatory actions or consultations from {", ".join(config.REGULATORS)}
   that affect capital raising or BFSI
4. Notable mandates or league-table moves by these banks:
   {", ".join(config.COMPETITOR_BANKS)}
5. Anything material about these PE firms in India:
   {", ".join(config.TARGET_FIRMS)}

Select the FIVE most significant items. Significance means: an ECM banker
covering Indian BFSI would want to know it before their morning call.
Ignore routine price moves, analyst target changes, and recycled stories.

If — and only if — genuinely nothing material happened, return an empty
items list. Do NOT pad with noise to reach five.

Respond with ONLY a JSON object, no preamble, no Markdown fences:

{{
  "items": [
    {{
      "headline": "one sharp line, max 15 words",
      "source": "publication name",
      "url": "link if available, else empty string",
      "significance": "one line: why this matters",
      "pitch_angle": "one line: how an ECM banker could act on this, or empty string if none",
      "tags": {{
        "companies": ["Company Name"],
        "deal_type": "IPO | QIP | OFS | M&A | Regulatory | PE | Other",
        "sector": "e.g. NBFC, Insurance, AMC, Bank, Fintech, Market Infra"
      }}
    }}
  ],
  "quiet_day": false,
  "one_line_read": "a single sentence summarising the day's tone for Indian ECM"
}}"""


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
