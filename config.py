"""Load config from environment."""
import os
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.
cache = {
    "path": os.getenv("CACHE_DIR"),
    "cache_time_gsheets": int(os.getenv("GSHEETS_CACHE")),
}
logbook = {
    "key": "1SRUaIhL17R-mVhbJb-52xE7_GQtU5kEKhuRAaTHB3FY",
    "auth_file": "service.json",
}
