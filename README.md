# ShoutCode — Free Texting Service

A clean, self-hosted web app for sending free SMS using:

- **Email-to-SMS gateways** (unlimited, no API key) — works for all major US carriers
- **TextBelt free tier** (1 message/day, no carrier selection needed)

---

## Quick Start

```bash
cd shoutcode
pip install -r requirements.txt
```

### Set credentials (for Email Gateway method)

Create a `.env` file or export these vars:

```bash
export SMTP_USER="your.gmail@gmail.com"
export SMTP_PASS="your-gmail-app-password"   # NOT your normal password
# SMTP_HOST defaults to smtp.gmail.com, SMTP_PORT defaults to 587
```

> **Gmail App Password:** Go to myaccount.google.com → Security → 2-Step Verification → App Passwords → create one for "Mail".

### Run

```bash
python app.py
# → http://localhost:5000
```

---

## Sending Methods

### 1. Email Gateway (unlimited, free)

Sends an email to `[phone]@carrier-gateway.com`. Your SMTP credentials are needed — the carrier's server delivers it as SMS.

Supported carriers:
| Carrier | Gateway |
|---|---|
| AT&T | `@txt.att.net` |
| Verizon | `@vtext.com` |
| T-Mobile | `@tmomail.net` |
| Sprint | `@messaging.sprintpcs.com` |
| Boost | `@sms.myboostmobile.com` |
| Cricket | `@sms.cricketwireless.net` |
| MetroPCS | `@mymetropcs.com` |
| US Cellular | `@email.uscc.net` |
| Virgin | `@vmobl.com` |

### 2. TextBelt (free tier)

Uses `https://textbelt.com/text` with key `textbelt` — 1 free SMS per day, no credentials needed. For more volume, set `TEXTBELT_KEY` to a paid key.

---

## API

### POST /send

```json
{
  "phone":   "5551234567",
  "message": "Hello from ShoutCode!",
  "method":  "gateway",     // "gateway" or "textbelt"
  "carrier": "att"          // required for gateway, ignored for textbelt
}
```

Response:
```json
{ "success": true, "method": "email-gateway", "gateway": "5551234567@txt.att.net" }
```

### GET /quota

Returns remaining TextBelt free quota for today.

---

## Deploy Free (options)

| Option | Notes |
|---|---|
| **Railway** | `railway up` — free tier, always-on |
| **Render** | Connect GitHub repo, free web service |
| **Fly.io** | `fly launch` — generous free tier |
| **Replit** | Import repo, run directly |

---

## File Structure

```
shoutcode/
├── app.py              ← Flask backend
├── requirements.txt
├── templates/
│   └── index.html      ← Frontend UI
└── static/
    ├── css/style.css
    └── js/app.js
```
