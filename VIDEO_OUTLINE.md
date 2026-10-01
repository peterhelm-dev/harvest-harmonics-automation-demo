# Video Outline — Harvest Harmonics 3-Tier Automation Demo

Target length: ~6-8 min. Tone: "I saw your job post, built this for free, here's
why I didn't just jump to the fanciest option."

---

## 0. Hook (0:00–0:30)

- Show the job posting screenshot on screen: Harvest Harmonics, "Go High Level
  Expert & AI Engineer."
- Line: "Instead of sending a resume, I built three working automations scoped
  to this exact company — their real pricing, their real scale problem. All in
  n8n instead of GHL on purpose — so it's easy to inspect and free to hand over,
  but every idea here maps 1:1 onto GHL workflows and AI employees."
- Show the GitHub repo page for 5 seconds (prove it's real, public, free).

## 1. Frame the three pain points (0:30–1:30)

Pull up the README table or just talk over it:

- **Tier 1 (simple):** every inbound lead needs a rep to manually look up which
  pricing tier applies — flat starter rate, per-acre small grower, YieldMAX,
  volume discount, or pivot program. That's from their *own public pricing page*.
- **Tier 2 (AI):** inbound messages are messy — skeptics, organic-certification
  questions, urgent post-install issues, plain price shoppers. Someone has to
  read every single one.
- **Tier 3 (app):** at 100+ farms on 2-year renewal cycles, "who renews when"
  and "who hasn't been touched in months" outgrows a spreadsheet.
- State the framing explicitly: "I'm going cheapest-tool-that-works at each
  step — you don't reach for AI or a custom app until the simple thing can't
  keep up anymore."

## 2. Tier 1 walkthrough — Lead & Pricing Router (1:30–3:00)

In n8n, with the imported workflow open:

- Point at the dummy data node: "this simulates 5 inbound leads — different
  acreage, different irrigation type, pivot vs drip."
- Click "Execute Workflow" (or run a single node) to show it firing.
- Open the Compute Pricing Tier code node — walk through 2-3 branches out loud:
  "4 acres of wine grapes, drip irrigation → starter rate, $1,000 flat. 380
  acres of corn on a pivot → that's the $20k pivot program, not a per-acre calc."
- Point at the IF node: "anything over 10 acres or a huge pivot gets routed to
  a human for a consult instead of an auto-quote — no AI needed anywhere in
  this one, it's just a lookup table nobody had written down."
- End: "this alone saves a rep the 2-minute lookup on every single lead."

## 3. Tier 2 walkthrough — Farmer Inquiry Triage (3:00–5:00)

In n8n, second imported workflow:

- Show the 5 dummy inquiries: "is this a scam," an organic-certification
  question, an urgent loose-fitting installation issue, a plain price request.
- Run it, open the Claude HTTP node, show the actual API call going out.
- Open the parsed output on 2 examples:
  - the urgent technical one → show it got flagged `is_urgent: true` and
    routed to the Slack/SMS alert branch
  - the organic-certification one → read the AI's drafted reply out loud,
    point out it's grounded in real facts (32 university trials, non-chemical)
    and explicitly tells the farmer to confirm with their own certifier —
    "it doesn't overpromise, it drafts something a human still approves."
- Call out the one real technical gotcha if you want to add credibility:
  "Claude wraps JSON in markdown fences even when you tell it not to — had to
  strip that before parsing, otherwise the whole thing silently breaks."

## 4. Tier 3 walkthrough — Farm Renewal Tracker (5:00–7:00)

Switch to the browser, localhost:5051:

- Show the full dashboard: summary cards (total farms, total acres, renewals
  due ≤60 days, lapsed, no-contact 180+ days).
- Point at the flag dots: "green/yellow/red on renewal date, and a second
  independent flag for last-contact gap — those move at different speeds,
  which is exactly the kind of thing that gets lost in a spreadsheet."
- Click "Draft Message" on the Ibanez Grove row (renewal due soon) — show the
  real Claude call happen live, read the drafted message: grounded in that
  farm's actual 22% documented yield result, correct day count to renewal.
- Click it again on the lapsed row (Lava Terrace Cellars) — show the message
  changes tone/purpose automatically (win-back vs renewal reminder) because
  the backend passes different context based on status.
- One line on durability: "seeds itself with realistic dummy data, SQLite
  file, zero setup beyond one pip install."

## 5. Close (7:00–7:30)

- "Repo's public and free regardless of what happens next: [github link]."
- "If the role's open, I'd want to build this for real inside your actual GHL
  account — but even if not, hope it's useful as-is."
- End on the GitHub repo URL on screen for a few seconds (pause to let people
  screenshot it).

---

## Recording checklist before hitting record

- [ ] Confirm localhost:5051 and localhost:5678 are both up (check both load
      before you start — they were just restarted)
- [ ] n8n: have both tier workflows already imported and open in two tabs/windows
- [ ] Tier 3: refresh the page once right before recording so seed data/dates
      look current
- [ ] Have the job posting screenshot ready to drop in at 0:00
- [ ] Have the GitHub repo tab pre-loaded, don't navigate to it live (avoid
      load-time dead air)
