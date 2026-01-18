import random

# ================= USER CONFIG =================

# Your reddit username
USERNAME = "Mobile7772"

# Copy your raw cookies from your browser and paste them here
COOKIES_RAW = """
csv=2; edgebucket=EXAMPLE; reddit_supported_media_codecs=EXAMPLE; eu_cookie={%22opted%22:true%2C%22nonessential%22:true}; theme=1; __stripe_mid=EXAMPLE; reddit_session=EXAMPLE; __stripe_sid=EXAMPLE; session_tracker=EXAMPLE"""

# Delay between delete requests (seconds)
DELETE_DELAY_MIN = 1.2
DELETE_DELAY_MAX = 2.5

# Delay between pagination fetches
PAGE_DELAY = 1.0

# Stop if this many delete failures occur
MAX_DELETE_ERRORS = 5

# ================= USER AGENTS =================

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; rv:123.0) Gecko/20100101 Firefox/123.0",
]

def random_user_agent():
    return random.choice(USER_AGENTS)

def random_delete_delay():
    return random.uniform(DELETE_DELAY_MIN, DELETE_DELAY_MAX)
