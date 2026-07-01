# scrapers/week1_trends.py
# WHAT THIS DOES: collects recent news about AI-ready networking, grouped into
# topics, and writes them to data/week1/trends.json for the Week 1 web page.
#
# It refreshes AT MOST once every 45 days. It remembers the last
# run in data/_state/last_run.json, so even if it is triggered more often, it
# quietly skips until 45 days have passed.
#
# TO USE YOUR OWN SOURCES: edit the FEEDS list below. Each line is
#   "Topic name you choose": "an RSS feed URL"
# Any RSS/Atom feed works (Google News searches, analyst blogs, industry sites).

import os
import re
import json
import datetime

import feedparser

from common import now_iso, write_json, record

STATE = "data/_state/last_run.json"
GATE_DAYS = 45

# Changeable links for various topics.
FEEDS = {
    "AI back-end / GPU fabric":
        "https://news.google.com/rss/search?q=%22AI+networking%22+data+center&hl=en-US&gl=US&ceid=US:en",
    "Network observability":
        "https://news.google.com/rss/search?q=network+observability+AI&hl=en-US&gl=US&ceid=US:en",
    "Cloud WAN / connectivity":
        "https://news.google.com/rss/search?q=cloud+WAN+enterprise+connectivity&hl=en-US&gl=US&ceid=US:en",
    "Ethernet vs proprietary fabric":
        "https://news.google.com/rss/search?q=Ethernet+AI+cluster+networking&hl=en-US&gl=US&ceid=US:en",
    "Data-centre buildout":
        "https://news.google.com/rss/search?q=AI+data+center+expansion+network&hl=en-US&gl=US&ceid=US:en",
}
# ------------------------------------------------------------------------------


def strip_html(text):
    """Turn a snippet of HTML into plain text for the tooltip bullets."""
    return re.sub(r"<[^>]+>", "", text or "").strip()


def due():
    """True only if 45+ days have passed since the last run (or it never ran)."""
    if not os.path.exists(STATE):
        return True
    last = json.load(open(STATE)).get("week1")
    if not last:
        return True
    age = datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(last)
    return age.days >= GATE_DAYS


def stamp_run():
    """Remember that we ran today, so the 45-day clock restarts."""
    s = json.load(open(STATE)) if os.path.exists(STATE) else {}
    s["week1"] = now_iso()
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    json.dump(s, open(STATE, "w"), indent=2)


if __name__ == "__main__":
    if not due():
        print("Week 1 not due yet (fewer than 45 days since last run). Skipping.")
        raise SystemExit(0)

    rows = []
    for topic, feed_url in FEEDS.items():
        parsed = feedparser.parse(feed_url)
        for e in parsed.entries[:25]:               # up to 25 findings per topic
            snippet = strip_html(e.get("summary", "")) or e.get("title", "")
            rows.append(record({
                "topic": topic,
                "headline": e.get("title", "(untitled)"),
                "summary_1": snippet[:180],          # the bullet text on the page
                "summary_2": e.get("published", ""), # when it was published
                "source_name": (e.get("source", {}) or {}).get("title", "news"),
            }, source_url=e.get("link", feed_url)))

    write_json("data/week1/trends.json", rows)
    stamp_run()
    print(f"Week 1 done: {len(rows)} findings across {len(FEEDS)} topics.")
