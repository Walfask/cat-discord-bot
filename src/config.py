import os
from pathlib import Path

TOKEN = os.environ["TOKEN"]
MAIN_SERVER_ID = os.environ["MAIN_SERVER_ID"]
MAIN_CHANNEL_ID = os.environ["MAIN_CHANNEL_ID"]
MAIN_USER_ID = os.environ["MAIN_USER_ID"]
CHANNEL_IDS = os.environ["CHANNEL_IDS"]
BASE_DIR = Path(__file__).resolve().parent.parent
PENDING_DIR = Path(BASE_DIR) / "images" / "pending"
SENT_DIR = Path(BASE_DIR) / "images" / "sent"
