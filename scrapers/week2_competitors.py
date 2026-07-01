# scrapers/week2_competitors.py
# WHAT THIS DOES: for each competitor, it finds their latest public move about
# AI networking (via a free news search) and pairs it with your own analyst
# rating of how mature they are. It writes data/week2/competitors.json for the
# Week 2 web page.
#
# IT WORKS OUT OF THE BOX. TWO THINGS YOU CAN EDIT:
#   1) COMPETITORS — the maturity score (1-5) is YOUR analyst judgment. Change
#      the numbers and the one-line "position" text to match your Week 2 study.
#   2) Nothing else is required. The "latest move" is fetched automatically.

import feedparser
from common import write_json, record

# ---- Subjective rating of industry level maturity. This can be edited as different companies change their positions. -----
COMPETITORS = {
    "Cisco":            {"maturity": 5, "position": "Broadest AI-networking portfolio; Ethernet + Silicon One."},
    "Juniper Networks": {"maturity": 5, "position": "AI-native ops (Mist) and strong data-center fabric."},
    "Lumen":            {"maturity": 3, "position": "Low-latency AI transport; network-as-a-service push."},
    "AT&T":             {"maturity": 3, "position": "Enterprise connectivity scale; measured AI messaging."},
    "Verizon Business": {"maturity": 3, "position": "Private networks and edge; growing AI narrative."},
    "NTT DATA":         {"maturity": 3, "position": "Global data-center footprint; systems-integration led."},
    "Orange Business":  {"maturity": 2, "position": "European strength; early AI-networking positioning."},
    "Tata Communications": {"maturity": 2, "position": "Global neutral transport; subsea + emerging markets = white space."},
}
# ------------------------------------------------------------------------------


def latest_move(company):
    """Find the company's most recent public headline about AI networking."""
    q = company.replace(" ", "+") + "+AI+network"
    url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    parsed = feedparser.parse(url)
    if parsed.entries:
        e = parsed.entries[0]
        return e.get("title", ""), e.get("published", ""), e.get("link", url)
    return "", "", url


if __name__ == "__main__":
    rows = []
    for name, info in COMPETITORS.items():
        headline, published, link = latest_move(name)
        rows.append(record({
            "name": name,
            "maturity": info["maturity"],       # 1-5, your analyst rating
            "position": info["position"],       # your one-line take
            "key_message": headline,            # their latest public move (auto)
            "last_move": published,
        }, source_url=link))

    write_json("data/week2/competitors.json", rows)
    print(f"Week 2 done: {len(rows)} competitors.")
