"""
config/settings.py
------------------
Central configuration for the AI Property Advisor.
Loads API keys from environment variables.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM Provider ─────────────────────────────────────────────────────────────
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama3-70b-8192")

# ── App Meta ──────────────────────────────────────────────────────────────────
APP_TITLE: str = "AI Property Advisor"
APP_TAGLINE: str = "Your intelligent real estate consultant — powered by AI"
APP_VERSION: str = "1.0.0"

# ── Agent Behavior ────────────────────────────────────────────────────────────
MAX_TURNS: int = 10            # maximum AutoGen round-trips per user message
TEMPERATURE: float = 0.4       # creativity vs determinism

# ── Validation ────────────────────────────────────────────────────────────────
if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY is not set. "
        "Add it to your .env file or export it as an environment variable."
    )