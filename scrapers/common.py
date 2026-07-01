# scrapers/common.py
# The shared engine every week reuses. It does three jobs:
#   1) fetch a web page politely (and only if robots.txt allows),
#   2) stamp every piece of data with WHERE it came from and WHEN,
#   3) write the result to a JSON file the web pages can read.


import os
import json
import time
import datetime
import urllib.robotparser
from urllib.parse import urlparse

import requests

UA = "TataIntelBot/1.0 (+https://github.com/akhilhnairprojects/ai-ready-networks-intel; research)"


def now_iso():
    """The current time, in a standard format, used as the 'retrieved_at' stamp."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def allowed(url):
    """Check the site's robots.txt before fetching an HTML page.
    Returns True only if the site permits it. If robots is unreachable,
    we play safe and return False."""
    p = urlparse(url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt")
    try:
        rp.read()
    except Exception:
        return False
    return rp.can_fetch(UA, url)


def get(url, **kw):
    """Fetch an HTML page politely: obey robots.txt, identify ourselves,
    and wait a second so we never hammer a site. Use this for scraping
    web PAGES. (For RSS feeds, use feedparser directly — feeds are meant
    to be read.)"""
    if not allowed(url):
        raise PermissionError(f"robots.txt disallows {url}")
    time.sleep(1)
    r = requests.get(url, headers={"User-Agent": UA}, timeout=30, **kw)
    r.raise_for_status()
    return r


def record(payload, source_url):
    """The one rule that makes everything verifiable: no fact leaves without
    a source link and a date attached. Wrap every row with this."""
    return {**payload, "source_url": source_url, "retrieved_at": now_iso()}


def write_json(path, rows):
    """Save the collected rows to a JSON file the web pages will read.
    Creates the folder if it does not exist yet."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"generated_at": now_iso(), "rows": rows}, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(rows)} rows to {path}")
