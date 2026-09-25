"""
Tier 3 -- Farm Installation & Renewal Tracker (local web app)

Stupid-simple stack: Flask + SQLite (built into Python), one AI call to
draft a renewal/check-in outreach message per farm. No deployment, no
signup, runs entirely on localhost.

Real pain point this solves: Harvest Harmonics has 100+ US farms (and
300+ worldwide) on 2-year YieldMAX program terms. Once you're past a
handful of installs, "who renews when" and "who hasn't been checked on"
stops fitting in a spreadsheet or a GHL pipeline view -- you need a
dashboard that flags renewals coming due and lets a human approve an
AI-drafted outreach message per farm.

SETUP:
    cd tier3-farm-renewal-tracker-app
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python app.py
    -> open http://localhost:5051

Requires ANTHROPIC_API_KEY in a .env file one directory up (../.env)
or in this folder -- python-dotenv checks both.
"""
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
import anthropic

# Load .env from this folder or the parent project folder
load_dotenv(Path(__file__).parent / ".env")
load_dotenv(Path(__file__).parent.parent / ".env")

APP_DIR = Path(__file__).parent
DB_PATH = APP_DIR / "farms.db"

app = Flask(__name__)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS farms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            farm_name TEXT NOT NULL,
            grower_name TEXT NOT NULL,
            state TEXT NOT NULL,
            crop TEXT NOT NULL,
            acreage INTEGER NOT NULL,
            program TEXT NOT NULL,
            install_date TEXT NOT NULL,
            renewal_date TEXT NOT NULL,
            last_yield_result TEXT DEFAULT '',
            last_contact_date TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'active',
            notes TEXT DEFAULT '',
            drafted_message TEXT DEFAULT ''
        )
        """
    )
    conn.commit()

    # Seed with realistic dummy rows on first run so the demo has content immediately.
    count = conn.execute("SELECT COUNT(*) FROM farms").fetchone()[0]
    if count == 0:
        today = datetime.now()
        seed_rows = [
            ("Barker Vineyards", "Duane Barker", "OR", "Wine Grapes", 4, "Starter (2yr)",
             today - timedelta(days=690), "Larger cluster size, best crop load ever per vine.",
             today - timedelta(days=95), "active", "Frequently shares photos, good case-study candidate."),
            ("Reed Family Citrus", "Jim Reed", "CA", "Citrus", 8, "Small Grower (annual)",
             today - timedelta(days=340), "Improved fruit quality, no hard yield number yet.",
             today - timedelta(days=20), "active", ""),
            ("Ibanez Grove", "Carla Ibanez", "FL", "Citrus", 22, "YieldMAX (2yr)",
             today - timedelta(days=705), "22% yield increase documented season 1.",
             today - timedelta(days=210), "active", "Renewal conversation not yet started -- past due."),
            ("Whitfield Farms", "Tom Whitfield", "NE", "Corn", 380, "Pivot Program (150ac zone)",
             today - timedelta(days=730), "18% yield increase, reduced fertilizer use ~15%.",
             today - timedelta(days=400), "active", "Two pivots total, only one zone renewed so far."),
            ("Dupont Potato Co", "Renee Dupont", "ID", "Potatoes", 45, "Volume Discount (2yr)",
             today - timedelta(days=50), "Too early for results.",
             today - timedelta(days=10), "active", "New install, first 30-day check-in due soon."),
            ("Lava Terrace Cellars", "Duane Barker", "OR", "Wine Grapes", 6, "Small Grower (annual)",
             today - timedelta(days=1000), "Long-term customer, consistent results.",
             today - timedelta(days=600), "lapsed", "Renewal date passed with no response -- needs win-back outreach."),
        ]
        for farm_name, grower, state, crop, acreage, program, install_date, yield_result, last_contact, status, notes in seed_rows:
            renewal_date = install_date + timedelta(days=730)  # 2-year program cycle
            conn.execute(
                """INSERT INTO farms
                   (farm_name, grower_name, state, crop, acreage, program, install_date,
                    renewal_date, last_yield_result, last_contact_date, status, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (farm_name, grower, state, crop, acreage, program,
                 install_date.strftime("%Y-%m-%d"), renewal_date.strftime("%Y-%m-%d"),
                 yield_result, last_contact.strftime("%Y-%m-%d"), status, notes),
            )
        conn.commit()
    conn.close()


def days_until(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return (d - datetime.now()).days


def renewal_flag(renewal_date, status):
    """Traffic-light flag for the dashboard based on renewal proximity."""
    if status == "lapsed":
        return "red"
    days = days_until(renewal_date)
    if days < 0:
        return "red"
    if days <= 60:
        return "yellow"
    return "green"


def contact_flag(last_contact_date):
    """Flag farms that haven't been touched in a while, independent of renewal."""
    if not last_contact_date:
        return "red"
    days = -days_until(last_contact_date)  # last_contact is in the past
    if days >= 180:
        return "red"
    if days >= 90:
        return "yellow"
    return "green"


@app.route("/")
def dashboard():
    conn = get_db()
    rows = conn.execute("SELECT * FROM farms ORDER BY renewal_date ASC").fetchall()
    conn.close()

    items = []
    for r in rows:
        d = dict(r)
        d["renewal_flag"] = renewal_flag(d["renewal_date"], d["status"])
        d["contact_flag"] = contact_flag(d["last_contact_date"])
        d["days_to_renewal"] = days_until(d["renewal_date"])
        items.append(d)

    summary = {
        "total_farms": len(items),
        "total_acres": sum(i["acreage"] for i in items),
        "renewals_due_60d": sum(1 for i in items if i["renewal_flag"] in ("yellow", "red") and i["status"] != "lapsed"),
        "lapsed": sum(1 for i in items if i["status"] == "lapsed"),
        "needs_checkin": sum(1 for i in items if i["contact_flag"] == "red"),
    }
    return render_template("dashboard.html", items=items, summary=summary, ai_enabled=bool(client))


@app.route("/add", methods=["POST"])
def add_entry():
    conn = get_db()
    install_date = request.form.get("install_date", datetime.now().strftime("%Y-%m-%d"))
    renewal_date = (datetime.strptime(install_date, "%Y-%m-%d") + timedelta(days=730)).strftime("%Y-%m-%d")
    conn.execute(
        """INSERT INTO farms
           (farm_name, grower_name, state, crop, acreage, program, install_date,
            renewal_date, last_contact_date, status, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)""",
        (
            request.form["farm_name"],
            request.form["grower_name"],
            request.form["state"],
            request.form["crop"],
            int(request.form["acreage"]),
            request.form["program"],
            install_date,
            renewal_date,
            datetime.now().strftime("%Y-%m-%d"),
            request.form.get("notes", ""),
        ),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/update_status/<int:item_id>", methods=["POST"])
def update_status(item_id):
    conn = get_db()
    conn.execute("UPDATE farms SET status = ? WHERE id = ?", (request.form["status"], item_id))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


@app.route("/draft_message/<int:item_id>", methods=["POST"])
def draft_message(item_id):
    """AI drafts a renewal or check-in outreach message for a specific farm. Staff reviews before sending."""
    conn = get_db()
    row = conn.execute("SELECT * FROM farms WHERE id = ?", (item_id,)).fetchone()

    if not client:
        conn.close()
        return jsonify({"error": "No ANTHROPIC_API_KEY found. Add it to your .env file and restart the app."}), 400

    days_to_renew = days_until(row["renewal_date"])
    if row["status"] == "lapsed":
        purpose = "a win-back message for a lapsed customer whose renewal date has already passed"
    elif days_to_renew <= 60:
        purpose = f"a renewal reminder ({days_to_renew} days until their program renewal date)"
    else:
        purpose = "a routine relationship check-in, not a renewal pitch"

    prompt = (
        f"Draft a warm, specific, professional outreach message from Harvest Harmonics to a farmer, "
        f"for the purpose of {purpose}. "
        f"Farm: {row['farm_name']}, grower {row['grower_name']}, {row['acreage']} acres of {row['crop']} in {row['state']}. "
        f"Program: {row['program']}. Installed: {row['install_date']}. "
        f"Documented result so far: {row['last_yield_result'] or 'not yet recorded'}. "
        f"Internal notes: {row['notes'] or 'none'}. "
        f"Reference the real Harvest Harmonics/Kyminasi Crop Booster facts only if relevant and true: "
        f"non-chemical biostimulant delivered through irrigation water, validated by 32 independent university "
        f"trials with 430 more underway, average documented yield increase 15-30%. "
        f"Do not fabricate results this specific farm hasn't reported. Keep it under 120 words, friendly, "
        f"grower-to-grower tone (not corporate), end with a clear single next step."
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    message_text = message.content[0].text

    conn.execute("UPDATE farms SET drafted_message = ? WHERE id = ?", (message_text, item_id))
    conn.commit()
    conn.close()

    return jsonify({"message": message_text})


if __name__ == "__main__":
    init_db()
    print("\n  Farm Renewal Tracker running: http://localhost:5051\n")
    app.run(debug=True, port=5051)
