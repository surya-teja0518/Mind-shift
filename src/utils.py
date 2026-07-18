import os
import logging
import sys
from typing import Optional, Tuple
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

def setup_logging() -> logging.Logger:
    """
    Configures and returns the central logger for MindShift.
    Outputs to standard stdout.
    """
    logger = logging.getLogger("mind_shift")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def get_logger() -> logging.Logger:
    """
    Retrieves the configured MindShift logger.
    """
    return logging.getLogger("mind_shift")

def get_gemini_api_key() -> Optional[str]:
    """
    Safely retrieves the GEMINI_API_KEY from:
    1. Streamlit secrets (for cloud deployments)
    2. OS environment variables (loaded via dotenv for local setup)
    """
    # 1. Check Streamlit Secrets (safely catch if streamlit is not running or secrets are missing)
    try:
        import streamlit as st
        if hasattr(st, "secrets") and st.secrets is not None:
            if "GEMINI_API_KEY" in st.secrets:
                return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

    # 2. Check OS Environment
    return os.getenv("GEMINI_API_KEY")

def get_gemini_model() -> str:
    """
    Retrieves the configured model name or defaults to gemini-2.5-flash.
    """
    return os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """
    Formats a floating point number as currency.
    """
    return f"{currency_symbol}{amount:.2f}"

def validate_environment_keys() -> Tuple[bool, str]:
    """
    Verifies that required API keys are available in secrets or environment.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return False, "GEMINI_API_KEY is not set. Please configure it in Streamlit Secrets, system environment, or a .env file."
    return True, ""
