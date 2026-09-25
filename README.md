# Harvest Harmonics — 3-Tier Automation Demo (n8n + AI)

Free, unsolicited build after seeing the ["Go High Level Expert & AI Engineer"](https://harvestharmonics.com/we-are-hiring/)
posting. Built in **n8n** (not GHL) to keep it public/importable and stack-agnostic —
every idea here maps directly onto GHL workflows/automations/AI employees.

No sales pitch, no ask — just three working demos scoped to real Harvest Harmonics
pain points, pulled from your own public pricing page and the job description itself.

## The three pain points (rising in stakes/complexity)

| Tier | Pain point | Why this level of tooling |
|---|---|---|
| **1 — Lead & Pricing Router** | Every inbound lead ("Start Boosting Your Crops Today" form) needs a rep to manually look up which pricing tier applies (flat $1,000 starter, $250/acre small grower, YieldMAX 10–29ac, volume discount 30+ac, or pivot program $10k/$20k) before replying. | Pure deterministic lookup table — no AI needed, cheap, instant, zero hallucination risk. Wiring this into GHL means the correct quote goes out in seconds instead of a rep's next free hour. |
| **2 — Farmer Inquiry Triage** | Inbound messages are messy and mixed: skeptics ("is this a scam"), organic-certification questions, urgent post-install technical issues, plain pricing requests. Right now someone has to read every single one and decide what matters. | This is where AI earns its keep — classifying open-ended text and drafting a grounded first-pass reply (using only real Harvest Harmonics facts: 32 university trials + 430 underway, 15–30% documented yield increase, non-chemical/irrigation-delivered) for a human to approve, while urgent technical issues get flagged immediately instead of sitting in a queue. |
| **3 — Farm Renewal Tracker (local app)** | At 100+ active US farms (300+ worldwide) on 2-year YieldMAX cycles, "who renews when" and "who hasn't been touched in 6 months" outgrows a spreadsheet or a GHL pipeline view. | A real dashboard: renewal-date and last-contact traffic lights across every farm, one-click AI-drafted renewal/check-in/win-back messages per farm (grounded in that farm's actual documented results, never fabricated). |

## What's in here

```
tier1-lead-pricing-router/      n8n workflow JSON — import via n8n → ⋯ menu → Import from File
tier2-farmer-inquiry-triage/    n8n workflow JSON — same import method
tier3-farm-renewal-tracker-app/ Local Flask + SQLite app, one command to run
.env.example                    Copy to .env, add your own Anthropic API key
```

## Running Tier 1 & 2 (n8n)

1. Open your n8n instance (self-hosted or cloud).
2. New Workflow → **⋯ menu → Import from File** → pick the `.json` in either tier folder.
3. Both ship with realistic **dummy data** hardcoded in a Code node, clearly labeled —
   swap that node for a real GHL webhook / Gmail trigger / website form in production.
4. Tier 2's HTTP Request node calls the Anthropic API directly with a manual
   `x-api-key` header (reads `$env.ANTHROPIC_API_KEY` — set that env var in your n8n
   instance, or swap in n8n's built-in Anthropic credential type).
5. Every workflow ends in a `NoOp` "MOCK SEND/LOG" node instead of a wired
   Slack/CRM/email node — safe to run as-is, obviously meant to be swapped for
   your real GHL/CRM nodes.

## Running Tier 3 (local app)

```bash
cd tier3-farm-renewal-tracker-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # then add your real Anthropic key
python app.py
# open http://localhost:5051
```

Seeds itself with 6 realistic dummy farms on first run — no setup needed to see it working.

## Why n8n instead of GHL for the demo

GHL is workflow automation + CRM + AI employees under one roof — same concepts
(triggers, conditional branches, AI steps, CRM actions) — but n8n keeps this
importable and inspectable by anyone without a GHL account, so it's easier
to hand over freely. The pricing logic, triage prompts, and renewal-tracking
data model transfer over 1:1 into GHL's workflow builder and Conversation AI.

---
Built by Peter Helm — [add contact/LinkedIn here]
