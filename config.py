# backend/config.py

import os

DB_URL = os.getenv("HIT_DB_URL", "sqlite:///./hit.db")
