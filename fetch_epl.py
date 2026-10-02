import requests
import json
import csv
import os
from datetime import datetime, timezone

url = "https://gamma-api.polymarket.com/events"

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

params = {
    "tag_id": 306,
    "end_date_min": now,
    "order": "volume",
    "ascending": "false",
    "limit": 100,
}

response = requests.get(url, params=params, timeout=10)
response.raise_for_status()
events = response.json()

print(len(events), "events")
rows = []
for event in events:
    title = event["title"]
    if " vs. " in title and " - " not in title and len(event["markets"]) == 3:
        home_team = title.split(" vs. ")[0]
        mids, bids, asks, vols = {}, {}, {}, {}
        for market in event["markets"]:
            prices = json.loads(market["outcomePrices"])
            question = market["question"]
            if "draw" in question.lower():
                key = "draw"
            elif question.startswith("Will " + home_team):
                key = "home"
            else:
                key = "away"
            mids[key] = float(prices[0])
            bids[key] = market.get("bestBid")
            asks[key] = market.get("bestAsk")
            vols[key] = market.get("volume")
        total = sum(mids.values())
        for key in ["home", "draw", "away"]:
            rows.append([now, title, event["endDate"], key, mids[key], bids[key],
                         asks[key], round(mids[key] / total, 4), vols[key]])

filename = "polymarket_snapshots.csv"
file_exists = os.path.exists(filename)
with open(filename, "a", newline="") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["snapshot_utc", "match", "end_date", "outcome", "mid",
                         "bid", "ask", "fair", "volume"])
    writer.writerows(rows)

print(len(rows), "rows saved to", filename)