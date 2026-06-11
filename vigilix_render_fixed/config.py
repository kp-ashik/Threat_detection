import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = "sentinelvision-context-secret"
DETECTION_INTERVAL = 8
CONFIDENCE = 0.35
CROWD_LIMIT = 5
ALERT_COOLDOWN_SECONDS = 25
HIGH_SPEED_PIXEL_THRESHOLD = 95

ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "")
ROBOFLOW_MODELS = {
    "weapon": os.getenv("WEAPON_MODEL_ID", ""),
    "fire_smoke": os.getenv("FIRE_SMOKE_MODEL_ID", ""),
    "helmet": os.getenv("HELMET_MODEL_ID", ""),
    "traffic": os.getenv("TRAFFIC_MODEL_ID", ""),
    "seatbelt": os.getenv("SEATBELT_MODEL_ID", ""),
    "theft": os.getenv("THEFT_MODEL_ID", "")
}

SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
