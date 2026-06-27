"""
ShoutCode - Free SMS Texting Service
Uses email-to-SMS carrier gateways (free, no API key needed)
+ TextBelt free tier as fallback
"""

from flask import Flask, render_template, request, jsonify
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os

app = Flask(__name__)

# ─── Carrier Gateway Map ───────────────────────────────────────────────────────
CARRIER_GATEWAYS = {
    "att":        "{number}@txt.att.net",
    "verizon":    "{number}@vtext.com",
    "tmobile":    "{number}@tmomail.net",
    "sprint":     "{number}@messaging.sprintpcs.com",
    "boost":      "{number}@sms.myboostmobile.com",
    "cricket":    "{number}@sms.cricketwireless.net",
    "metropcs":   "{number}@mymetropcs.com",
    "uscellular": "{number}@email.uscc.net",
    "virgin":     "{number}@vmobl.com",
    "straight":   "{number}@vtext.com",
}

# ─── Config (set via environment variables) ────────────────────────────────────
SMTP_HOST     = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER     = os.environ.get("SMTP_USER", "")      # your Gmail address
SMTP_PASS     = os.environ.get("SMTP_PASS", "")      # Gmail App Password
TEXTBELT_KEY  = os.environ.get("TEXTBELT_KEY", "textbelt")  # "textbelt" = free tier (1/day)


def clean_phone(number: str) -> str:
    """Strip everything except digits."""
    return re.sub(r"\D", "", number)


def send_via_gateway(phone: str, carrier: str, message: str) -> dict:
    """Send SMS via carrier email gateway — completely free."""
    if not SMTP_USER or not SMTP_PASS:
        return {"success": False, "error": "SMTP credentials not configured. Set SMTP_USER and SMTP_PASS env vars."}

    gateway = CARRIER_GATEWAYS.get(carrier.lower())
    if not gateway:
        return {"success": False, "error": f"Unknown carrier: {carrier}"}

    phone_clean = clean_phone(phone)
    sms_email = gateway.format(number=phone_clean)

    try:
        msg = MIMEText(message)
        msg["From"]    = SMTP_USER
        msg["To"]      = sms_email
        msg["Subject"] = ""   # Keep subject empty for clean SMS

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, sms_email, msg.as_string())

        return {"success": True, "method": "email-gateway", "gateway": sms_email}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_via_textbelt(phone: str, message: str) -> dict:
    """Send SMS via TextBelt API. Free tier = 1 message/day."""
    phone_clean = clean_phone(phone)
    try:
        resp = requests.post(
            "https://textbelt.com/text",
            data={
                "phone":   phone_clean,
                "message": message,
                "key":     TEXTBELT_KEY,
            },
            timeout=10,
        )
        data = resp.json()
        if data.get("success"):
            return {"success": True, "method": "textbelt", "quotaRemaining": data.get("quotaRemaining")}
        else:
            return {"success": False, "error": data.get("error", "TextBelt failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    carriers = list(CARRIER_GATEWAYS.keys())
    return render_template("index.html", carriers=carriers)


@app.route("/send", methods=["POST"])
def send():
    data    = request.get_json()
    phone   = data.get("phone", "").strip()
    message = data.get("message", "").strip()
    method  = data.get("method", "gateway")   # "gateway" or "textbelt"
    carrier = data.get("carrier", "")

    if not phone or not message:
        return jsonify({"success": False, "error": "Phone and message are required."}), 400

    if len(message) > 160:
        return jsonify({"success": False, "error": "Message must be 160 characters or fewer."}), 400

    if method == "gateway":
        if not carrier:
            return jsonify({"success": False, "error": "Please select a carrier for gateway delivery."}), 400
        result = send_via_gateway(phone, carrier, message)
    else:
        result = send_via_textbelt(phone, message)

    status_code = 200 if result["success"] else 500
    return jsonify(result), status_code


@app.route("/carriers")
def carriers():
    return jsonify({"carriers": list(CARRIER_GATEWAYS.keys())})


@app.route("/quota")
def quota():
    """Check TextBelt remaining quota."""
    try:
        resp = requests.get(f"https://textbelt.com/quota/{TEXTBELT_KEY}", timeout=5)
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🔊 ShoutCode running on http://localhost:{port}")
    app.run(debug=True, host="0.0.0.0", port=port)
