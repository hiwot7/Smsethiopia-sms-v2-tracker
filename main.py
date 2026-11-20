import os
from datetime import datetime, timezone
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import httpx

from database import get_db, init_db

load_dotenv()

API_KEY = os.getenv("SMSETHIOPIA_API_KEY")
BASE_URL = os.getenv("SMSETHIOPIA_BASE_URL", "https://smsethiopia.com/api/v2")

app = FastAPI(title="SMS Ethiopia API v2 - Clinic Reminder Tracker")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup():
    init_db()

# 1. Dashboard View
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    conn = get_db()
    reminders = conn.execute("SELECT * FROM reminders ORDER BY id DESC").fetchall()
    conn.close()
    return templates.TemplateResponse("index.html", {"request": request, "reminders": reminders})

# 2. Send Outbound SMS (POST /api/v2/sms/send)
@app.post("/send")
async def send_reminder(
    patient_name: str = Form(...),
    msisdn: str = Form(...),
    message_text: str = Form(...)
):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    headers = {
        "KEY": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "msisdn": msisdn.strip(),
        "text": message_text.strip()
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(f"{BASE_URL}/sms/send", json=payload, headers=headers)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"SMS API Error: {resp.text}")

    data = resp.json()
    sms_ulid = data.get("id")
    segments = data.get("segments", 1)
    status = data.get("status", "ACCEPTED")

    conn = get_db()
    conn.execute(
        """
        INSERT INTO reminders (patient_name, msisdn, message_text, sms_ulid, segments, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (patient_name.strip(), msisdn.strip(), message_text.strip(), sms_ulid, segments, status, now, now)
    )
    conn.commit()
    conn.close()

    return RedirectResponse(url="/", status_code=303)

# 3. Poll Status Lookup (GET /api/v2/sms/{id})
@app.post("/sync/{sms_ulid}")
async def sync_status(sms_ulid: str):
    headers = {"KEY": API_KEY}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{BASE_URL}/sms/{sms_ulid}", headers=headers)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Status Lookup Error: {resp.text}")

    data = resp.json()
    new_status = data.get("status")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    if new_status:
        conn = get_db()
        conn.execute(
            "UPDATE reminders SET status = ?, updated_at = ? WHERE sms_ulid = ?",
            (new_status, now, sms_ulid)
        )
        conn.commit()
        conn.close()

    return RedirectResponse(url="/", status_code=303)

# 4. Delivery Report Webhook Receiver (POST /webhooks/sms-dlr)
@app.post("/webhooks/sms-dlr")
async def delivery_webhook(request: Request):
    payload = await request.json()
    sms_ulid = payload.get("id")
    status = payload.get("status")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    if sms_ulid and status:
        conn = get_db()
        conn.execute(
            "UPDATE reminders SET status = ?, updated_at = ? WHERE sms_ulid = ?",
            (status, now, sms_ulid)
        )
        conn.commit()
        conn.close()

    # Return 200 OK immediately (must respond within 5s per API docs)
    return {"received": True, "id": sms_ulid, "status": status}