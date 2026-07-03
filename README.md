# The Issue Ledger

An autonomous daily system for an Indian ECM/BFSI banker. Zero required
input. Three engines run before you wake up; you read for 60 seconds, or
you don't — nothing breaks either way.

**Be clear about what this is:** a small backend project, not a static
page. A page cannot update itself without something running on a schedule
with an API key. The trick used here is that GitHub gives you both halves
free — **GitHub Actions** is the scheduled server, **GitHub Pages** is the
hosting — so there is no machine to maintain and nothing to pay for except
API usage (one Sonnet call with a handful of web searches plus two small
calls per day; check current pricing at https://docs.claude.com, but it is
pocket change).

## The engines

| Engine | What it does | Input required |
|---|---|---|
| 1 · Market Pulse | 6:30 IST cron → Claude + web search → 5 most significant Indian ECM/BFSI/regulatory items, each with a pitch angle. On a genuinely empty day the page says **"Quiet day — nothing material"** — it never pads with noise. | None |
| 2 · Coaching card | Rotates daily: technical teach → behavioral teach → sensei reflection. Each card poses the question **and immediately gives the worked answer** — you read, you never type. No streaks, no chains. | None |
| 3 · Knowledge bank | Every pulse item is classified and filed into `data/knowledge_bank.json` (entity → dated notes → deal-type/sector tags), rendered as a searchable page. Compounds into a proprietary reference over months with zero manual entry. | None |
| 4 · Personal ledger (optional) | The one thing that structurally cannot self-generate: what *you* decided. A Telegram message or voice note → Cloudflare Worker → classified and filed. See `engine4/`. The system is fully valuable without it. | One message, when you feel like it |

What this deliberately does **not** do: invent a "decision ledger" from
market news. An AI cannot infer your private reasoning, and pretending
otherwise would be misleading, not helpful.

## Deploy (~15 minutes, once)

1. **Create a repo** — push this folder to a new GitHub repository
   (private is fine; Pages works on private repos on paid plans, public
   repos on free — the page contains only public market data, so a public
   repo is safe).

2. **Add the API key** — repo → Settings → Secrets and variables →
   Actions → New repository secret → name `ANTHROPIC_API_KEY`, value your
   key from https://console.anthropic.com. The key lives server-side in
   GitHub's secret store; it never appears in the page or the repo.
   Enable **web search** for your org in the Console (Settings) if it
   isn't already.

3. **Enable Pages** — repo → Settings → Pages → Source: **GitHub Actions**.

4. **Test** — Actions tab → "Daily brief" → **Run workflow**. Two minutes
   later your page is live at `https://<user>.github.io/<repo>/`.
   Bookmark it on your phone's home screen. From tomorrow it is simply
   already updated when you open it.

That's the whole deployment. The cron in `.github/workflows/daily.yml`
fires at 01:00 UTC (06:30 IST); GitHub's scheduler can drift a few
minutes, which doesn't matter for this use.

**Email instead of (or as well as) the page:** uncomment the email step in
`daily.yml` and add Gmail app-password secrets. The page needs no login;
email is optional convenience.

## Files

```
config.py        the only file you routinely edit (profile, firm lists, model)
prompts.py       all engine prompts
engines.py       API calls + knowledge-bank merge logic
render.py        the two pages (ledger/terminal aesthetic)
run_daily.py     orchestrator (isolated failures degrade gracefully)
data/            knowledge bank + daily JSON archive (committed by the bot)
site/            generated HTML (deployed to Pages)
engine4/         optional Telegram capture worker
```

## Run locally

```bash
pip install -r requirements.txt
ANTHROPIC_API_KEY=sk-... python run_daily.py
open site/index.html
```

## Honest limitations

- **Cron drift:** GitHub schedules are best-effort; the run may land at
  6:35 or 6:45 IST. Irrelevant for a morning brief.
- **Model output is JSON-by-instruction**, parsed defensively; a malformed
  day degrades to an honest error card, never a blank page.
- **The knowledge bank is only as good as the day's press.** It's a
  compounding reference of public information — it will never contain your
  private deal reasoning unless you use Engine 4.
- **Engine 4 requires a separately hosted webhook** (Cloudflare Workers
  free tier) because Telegram must be able to reach an always-on URL —
  a scheduled Action can't receive webhooks.
