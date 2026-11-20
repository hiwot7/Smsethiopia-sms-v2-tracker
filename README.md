# SMS Ethiopia API v2 – Clinic Reminder Tracker

A lightweight FastAPI + SQLite web application demonstrating real-world integration with the **SMS Ethiopia API v2**.

## Features
- **Outbound SMS (`POST /api/v2/sms/send`):** Sends patient appointment reminders (supports English GSM-7 and Amharic UCS-2) using the `KEY` authentication header.
- **ULID & Segment Tracking:** Stores the sortable ULID (`id`), exact segment count (`segments`), and initial `ACCEPTED` state returned by API v2.
- **Status Polling (`GET /api/v2/sms/{id}`):** One-click status reconciliation (`ACCEPTED` → `SENT` → `DELIVERED` / `UNDELIVERED`).
- **Delivery Report Webhook (`POST /webhooks/sms-dlr`):** Receives real-time final delivery callbacks and flags undelivered reminders for manual follow-up.

## Quick Start

1. **Clone and set up environment:**
   ```bash
   git clone [https://github.com/hiwot7/sms-v2-tracker.git](https://github.com/hiwot7/sms-v2-tracker.git)
   cd sms-v2-tracker
   python -m venv venv
   source venv/Scripts/activate   # Windows Git Bash (or: .\venv\Scripts\Activate.ps1 in PowerShell)
   pip install -r requirements.txt
