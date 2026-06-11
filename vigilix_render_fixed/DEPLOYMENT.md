# Vigilix AI — Complete Render Deployment Guide

## Why It Was Failing (Root Causes Fixed)

| # | Problem | Fix Applied |
|---|---------|-------------|
| 1 | `opencv-python` pulls GUI libs that crash on Render's headless Linux | Changed to `opencv-python-headless` |
| 2 | SQLite DB written to working dir which may be read-only on Render | DB now stored at `/tmp/vigilix.db` |
| 3 | `evidence/` folder written to read-only working dir | Evidence now stored at `/tmp/evidence/` |
| 4 | `init_db()` only called inside `if __name__ == "__main__"` — Gunicorn never ran it | Moved `init_db()` to module level |
| 5 | Duplicate `import os` at module level caused a silent parse issue | Cleaned up |
| 6 | Unpinned packages caused version mismatches during build | All packages now pinned |

---

## No — You Do NOT Need a Separate Backend

This is a single Flask app. Frontend (HTML templates) and backend (Python/Flask) run together in one Render Web Service. One deployment is all you need.

---

## Step-by-Step: Deploy to Render

### Step 1 — Push to GitHub

```bash
cd your-project-folder
git init
git add .
git commit -m "Vigilix AI - ready for Render"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/vigilix-ai.git
git push -u origin main
```

### Step 2 — Create Web Service on Render

1. Go to https://render.com → Sign in
2. Click **New +** → **Web Service**
3. Click **Connect a repository** → select your GitHub repo
4. Render auto-detects `render.yaml`. Confirm:
   - **Name:** vigilix-ai
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT`
   - **Plan:** Free

### Step 3 — Set Environment Variables

In Render Dashboard → your service → **Environment** tab, add these:

| Variable | Value | Required? |
|---|---|---|
| `SECRET_KEY` | any long random string e.g. `vigilix-super-secret-2024` | YES |
| `DB_PATH` | `/tmp/vigilix.db` | YES |
| `EVIDENCE_DIR` | `/tmp/evidence` | YES |
| `ROBOFLOW_API_KEY` | your key from roboflow.com | For AI detection |
| `WEAPON_MODEL_ID` | e.g. `weapon-detection/3` | For AI detection |
| `FIRE_SMOKE_MODEL_ID` | e.g. `fire-smoke-detection/2` | Optional |
| `HELMET_MODEL_ID` | e.g. `helmet-detection/1` | Optional |
| `TRAFFIC_MODEL_ID` | e.g. `traffic-violation/1` | Optional |
| `SEATBELT_MODEL_ID` | e.g. `seatbelt-detection/1` | Optional |
| `THEFT_MODEL_ID` | e.g. `theft-detection/1` | Optional |
| `SMTP_EMAIL` | your Gmail address | For email alerts |
| `SMTP_PASSWORD` | Gmail App Password (not your login password) | For email alerts |

> **Gmail App Password:** Go to myaccount.google.com → Security → 2-Step Verification → App passwords → create one for "Mail"

### Step 4 — Deploy

Click **Create Web Service**. Render will:
1. Clone your repo
2. Run `pip install -r requirements.txt` (~2-3 minutes first time)
3. Start Gunicorn
4. Give you a live URL like `https://vigilix-ai.onrender.com`

---

## Important Limitations on Free Tier

| Limitation | Detail |
|---|---|
| **Sleep after 15 min inactivity** | First visit after sleep takes ~30 seconds to wake up |
| **Ephemeral storage** | `/tmp` is wiped on every redeploy/restart — DB and evidence images are lost |
| **No local webcam** | `source: 0` (laptop camera) won't work on Render. Use RTSP URLs only |
| **512 MB RAM** | Large YOLO models may OOM. The app gracefully falls back if model fails to load |

### For persistent data (recommended for real use):
- Upgrade to **Starter plan** ($7/mo) and add a **Render Disk** mounted at `/data`
- Then set env vars: `DB_PATH=/data/vigilix.db` and `EVIDENCE_DIR=/data/evidence`

---

## Camera Sources That Work on Render

| Source | Example | Works on Render? |
|---|---|---|
| RTSP IP camera | `rtsp://192.168.1.100:554/stream` | YES |
| HTTP stream | `http://192.168.1.100:8080/video` | YES |
| YouTube/public stream URL | full URL | YES |
| Video file URL | `https://example.com/video.mp4` | YES |
| Webcam index `0` | `0` | NO (no hardware) |

---

## Local Development

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # fill in your keys
python app.py
# Visit http://localhost:5000
```
