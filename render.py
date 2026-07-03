"""
Renders site/index.html (today's brief) and site/bank.html (knowledge bank).

Design system — "issue ledger":
  Ink    #0C0F12  page background (blue-black, not pure black)
  Panel  #12161B  cards
  Rule   #262E36  hairlines
  Paper  #E9E3D3  primary text (prospectus cream)
  Dim    #8B9299  secondary text
  Brass  #C9A570  accent (tombstone gilt)
  Sage   #86A88B  quiet-day / calm marker

Type: Fraunces (display serif), Spectral (reading serif), IBM Plex Mono
(labels, tickers, data). Signature device: prospectus double-rule masthead
and folio-numbered ledger entries.
"""

import html
import json
import os
from datetime import date

SITE_DIR = os.path.join(os.path.dirname(__file__), "site")


def esc(s: str) -> str:
    return html.escape(str(s or ""))


CSS = """
:root{
  --ink:#0C0F12; --panel:#12161B; --rule:#262E36;
  --paper:#E9E3D3; --dim:#8B9299; --brass:#C9A570; --sage:#86A88B;
}
*{margin:0;padding:0;box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{background:var(--ink);color:var(--paper);
  font-family:'Spectral',Georgia,serif;font-size:16px;line-height:1.6}
a{color:var(--brass);text-decoration:none;border-bottom:1px solid var(--rule)}
a:hover,a:focus-visible{border-bottom-color:var(--brass);outline:none}
.wrap{max-width:740px;margin:0 auto;padding:40px 22px 80px}
.mono{font-family:'IBM Plex Mono',ui-monospace,monospace}

/* masthead — prospectus double rule */
.masthead{border-top:3px solid var(--paper);position:relative;padding-top:7px}
.masthead::before{content:"";display:block;border-top:1px solid var(--paper);
  margin-bottom:22px}
.mast-row{display:flex;justify-content:space-between;align-items:baseline;
  flex-wrap:wrap;gap:6px}
.mast-title{font-family:'Fraunces',Georgia,serif;font-weight:600;
  font-size:30px;letter-spacing:.01em}
.mast-title em{font-style:italic;color:var(--brass);font-weight:500}
.mast-meta{font-family:'IBM Plex Mono',monospace;font-size:11px;
  color:var(--dim);letter-spacing:.14em;text-transform:uppercase}
.readline{margin:14px 0 0;color:var(--dim);font-style:italic;font-size:15px}

/* section labels */
.seclabel{font-family:'IBM Plex Mono',monospace;font-size:11px;
  letter-spacing:.22em;text-transform:uppercase;color:var(--brass);
  margin:52px 0 6px;display:flex;align-items:center;gap:12px}
.seclabel::after{content:"";flex:1;border-top:1px solid var(--rule)}

/* ledger entries */
.entry{display:grid;grid-template-columns:44px 1fr;gap:0 14px;
  padding:20px 0;border-bottom:1px solid var(--rule)}
.folio{font-family:'IBM Plex Mono',monospace;font-size:13px;color:var(--dim);
  padding-top:5px}
.headline{font-family:'Fraunces',Georgia,serif;font-weight:500;font-size:19px;
  line-height:1.35}
.sig{color:var(--dim);font-size:15px;margin-top:6px}
.pitch{margin-top:9px;font-size:14.5px;color:var(--brass)}
.pitch::before{content:"\\2192  pitch \\00b7 ";font-family:'IBM Plex Mono',monospace;
  font-size:11px;letter-spacing:.12em;text-transform:uppercase}
.tags{margin-top:9px;display:flex;flex-wrap:wrap;gap:7px}
.tag{font-family:'IBM Plex Mono',monospace;font-size:10.5px;color:var(--dim);
  border:1px solid var(--rule);padding:2px 7px;letter-spacing:.06em}
.tag.deal{color:var(--brass);border-color:#3a3428}
.src{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--dim);
  margin-top:8px}
.quiet{padding:34px 0;border-bottom:1px solid var(--rule);
  font-family:'Fraunces',Georgia,serif;font-size:18px;color:var(--sage);
  font-style:italic}

/* coaching card */
.card{background:var(--panel);border-left:2px solid var(--brass);
  padding:26px 26px 28px;margin-top:10px}
.card .mode{font-family:'IBM Plex Mono',monospace;font-size:10.5px;
  letter-spacing:.2em;text-transform:uppercase;color:var(--dim)}
.card h2{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:21px;
  margin:8px 0 14px}
.card .q{font-style:italic;color:var(--paper);border-bottom:1px solid var(--rule);
  padding-bottom:14px;margin-bottom:14px}
.card .teach p{margin-bottom:12px;font-size:15.5px;color:#D8D2C3}
.card .teach p:last-child{margin-bottom:0}

/* footer */
.foot{margin-top:64px;border-top:1px solid var(--rule);padding-top:14px;
  display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;
  font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--dim);
  letter-spacing:.1em;text-transform:uppercase}

/* knowledge bank */
.search{width:100%;background:var(--panel);border:1px solid var(--rule);
  color:var(--paper);font-family:'IBM Plex Mono',monospace;font-size:14px;
  padding:11px 14px;margin:18px 0 8px}
.search:focus-visible{outline:1px solid var(--brass)}
.entity{padding:22px 0;border-bottom:1px solid var(--rule)}
.entity h3{font-family:'Fraunces',Georgia,serif;font-weight:600;font-size:19px;
  display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
.entity h3 .etype{font-family:'IBM Plex Mono',monospace;font-size:10.5px;
  color:var(--dim);letter-spacing:.14em;text-transform:uppercase;font-weight:400}
.note{display:grid;grid-template-columns:86px 1fr;gap:0 14px;margin-top:12px}
.note .d{font-family:'IBM Plex Mono',monospace;font-size:11.5px;color:var(--dim);
  padding-top:3px}
.note .n{font-size:15px;color:#D8D2C3}
.note .n .m{font-family:'IBM Plex Mono',monospace;font-size:10.5px;
  color:var(--dim);letter-spacing:.06em}
.count{font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--dim);
  letter-spacing:.12em;text-transform:uppercase;margin-bottom:4px}
@media(max-width:520px){
  .entry{grid-template-columns:30px 1fr}
  .note{grid-template-columns:1fr}.note .d{padding:0 0 2px}
  .mast-title{font-size:24px}
}
@media(prefers-reduced-motion:no-preference){
  .entry,.card,.entity{animation:rise .5s ease both}
  @keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1}}
}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400..700;1,400..600'
         '&family=Spectral:ital,wght@0,300;0,400;1,400&family=IBM+Plex+Mono:wght@400;500'
         '&display=swap" rel="stylesheet">')


def _page(title: str, body: str) -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<title>{esc(title)}</title>{FONTS}<style>{CSS}</style></head>
<body><div class="wrap">{body}</div></body></html>"""


def _masthead(today: date, sub: str) -> str:
    return f"""<header class="masthead">
  <div class="mast-row">
    <div class="mast-title">The Issue <em>Ledger</em></div>
    <div class="mast-meta">Session · {today.strftime('%d %b %Y').upper()} · Mumbai</div>
  </div>
  <p class="readline">{esc(sub)}</p>
</header>"""


def render_index(today: date, pulse: dict, card: dict) -> None:
    # --- pulse entries -----------------------------------------------------
    if pulse.get("quiet_day"):
        entries = '<div class="quiet">Quiet day — nothing material.</div>'
    else:
        rows = []
        for i, it in enumerate(pulse.get("items", []), 1):
            tags = it.get("tags", {}) or {}
            chips = "".join(
                f'<span class="tag">{esc(c)}</span>'
                for c in (tags.get("companies") or [])
            )
            if tags.get("deal_type"):
                chips = f'<span class="tag deal">{esc(tags["deal_type"])}</span>' + chips
            if tags.get("sector"):
                chips += f'<span class="tag">{esc(tags["sector"])}</span>'
            pitch = (f'<div class="pitch">{esc(it["pitch_angle"])}</div>'
                     if it.get("pitch_angle") else "")
            src = esc(it.get("source", ""))
            if it.get("url"):
                src = f'<a href="{esc(it["url"])}" rel="noopener">{src}</a>'
            rows.append(f"""<article class="entry">
  <div class="folio">{i:02d}</div>
  <div>
    <div class="headline">{esc(it.get("headline",""))}</div>
    <div class="sig">{esc(it.get("significance",""))}</div>
    {pitch}
    <div class="tags">{chips}</div>
    <div class="src">{src}</div>
  </div>
</article>""")
        entries = "".join(rows)

    # --- coaching card -----------------------------------------------------
    mode_label = {"technical": "Technical teach", "behavioral": "Fit & behavioral",
                  "sensei": "Sensei reflection"}.get(card.get("mode", ""), "Coaching")
    teach = "".join(f"<p>{esc(p)}</p>"
                    for p in (card.get("teaching", "")).split("\n\n") if p.strip())
    card_html = f"""<section class="card">
  <div class="mode">{esc(mode_label)}</div>
  <h2>{esc(card.get("title",""))}</h2>
  <div class="q">{esc(card.get("question",""))}</div>
  <div class="teach">{teach}</div>
</section>"""

    body = (
        _masthead(today, pulse.get("one_line_read", ""))
        + '<div class="seclabel">Market pulse</div>' + entries
        + '<div class="seclabel">Coaching card</div>' + card_html
        + f"""<footer class="foot">
  <span><a href="bank.html">Knowledge bank →</a></span>
  <span>Generated before you woke up</span>
</footer>"""
    )
    os.makedirs(SITE_DIR, exist_ok=True)
    with open(os.path.join(SITE_DIR, "index.html"), "w") as f:
        f.write(_page(f"The Issue Ledger · {today.isoformat()}", body))


def render_bank(today: date, bank: dict) -> None:
    entities = bank.get("entities", {})
    n_entries = sum(len(e.get("entries", [])) for e in entities.values())

    blocks = []
    # newest activity first
    def latest(e):
        ds = [x.get("date", "") for x in e.get("entries", [])]
        return max(ds) if ds else ""
    for slug, ent in sorted(entities.items(), key=lambda kv: latest(kv[1]), reverse=True):
        notes = []
        for x in sorted(ent.get("entries", []), key=lambda x: x.get("date", ""), reverse=True):
            src = esc(x.get("source", ""))
            if x.get("url"):
                src = f'<a href="{esc(x["url"])}" rel="noopener">{src}</a>'
            meta = " · ".join(v for v in [x.get("deal_type"), x.get("sector")] if v)
            notes.append(f"""<div class="note"><div class="d">{esc(x.get("date",""))}</div>
<div class="n">{esc(x.get("note",""))}
<div class="m">{esc(meta)}{" · " if meta and src else ""}{src}</div></div></div>""")
        haystack = esc(" ".join([
            ent.get("name",""), ent.get("type",""), slug,
            " ".join(x.get("note","") + " " + str(x.get("deal_type","")) + " "
                     + str(x.get("sector","")) for x in ent.get("entries", []))
        ]).lower())
        blocks.append(f"""<section class="entity" data-h="{haystack}">
  <h3>{esc(ent.get("name", slug))} <span class="etype">{esc(ent.get("type",""))}
  · {len(ent.get("entries",[]))} note{"s" if len(ent.get("entries",[]))!=1 else ""}</span></h3>
  {''.join(notes)}
</section>""")

    body = (
        _masthead(today, "Everything worth knowing about Indian BFSI capital markets, continuously updated.")
        + f'<div class="seclabel">Knowledge bank</div>'
        + f'<div class="count">{len(entities)} entities · {n_entries} notes</div>'
        + '<input class="search" id="q" type="search" placeholder="filter — company, deal type, sector, keyword" aria-label="Filter knowledge bank">'
        + "".join(blocks)
        + """<footer class="foot"><span><a href="index.html">← Today's brief</a></span>
<span>Compounds daily · zero manual entry</span></footer>
<script>
const q=document.getElementById('q');
q.addEventListener('input',()=>{const v=q.value.trim().toLowerCase();
for(const s of document.querySelectorAll('.entity'))
  s.style.display=!v||s.dataset.h.includes(v)?'':'none';});
</script>"""
    )
    with open(os.path.join(SITE_DIR, "bank.html"), "w") as f:
        f.write(_page("Knowledge Bank · The Issue Ledger", body))
