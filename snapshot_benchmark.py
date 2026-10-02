import os
import csv
import time
import requests
from datetime import datetime, timezone, timedelta

key = os.environ["ODDSPAPI_KEY"]
BASE = "https://api.oddspapi.io/v4"
OUTCOMES = {"home": "101", "draw": "102", "away": "103"}
DAYS_AHEAD = 11
cutoff = (datetime.now(timezone.utc) + timedelta(days=DAYS_AHEAD)).strftime("%Y-%m-%dT%H:%M:%S")

def normalize(probs):
    total = sum(probs.values())
    return {name: p / total for name, p in probs.items()}

def pinnacle_fair(market):
    raw = {}
    for name, code in OUTCOMES.items():
        raw[name] = 1 / market["outcomes"][code]["players"]["0"]["price"]
    return normalize(raw)

def betfair_fair(market):
    raw, backs, lays = {}, {}, {}
    for name, code in OUTCOMES.items():
        meta = market["outcomes"][code]["players"]["0"]["exchangeMeta"]
        backs[name] = meta["availableToBack"][0]["price"]
        lays[name] = meta["availableToLay"][0]["price"]
        raw[name] = (1 / backs[name] + 1 / lays[name]) / 2
    return normalize(raw), backs, lays

response = requests.get(
    BASE + "/fixtures", 
    params={"apiKey": key, "tournamentId": 17, "statusId": 0, 
            "hasOdds": "true", "bookmakers": "pinnacle"},
    timeout=10,
)
response.raise_for_status()
fixtures = response.json()
print(len(fixtures), "fixtures returned | cutoff:", cutoff)

rows = []
for fx in fixtures:
    if fx["startTime"][:19] > cutoff:
        continue
    match = fx["participant1Name"] + " vs " + fx["participant2Name"]
    resp = requests.get(
        BASE + "/odds",
        params={"apiKey": key, "fixtureId": fx["fixtureId"], "bookmakers": "pinnacle,betfair-ex", "oddsFormat": "decimal"},
        timeout=10,
    )
    fetched = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    time.sleep(1)
    if resp.status_code != 200:
        print(match, "| failed with status", resp.status_code)
        continue
    books = resp.json()["bookmakerOdds"]
    try:
        pin_market = books["pinnacle"]["markets"]["101"]
        bf_market = books["betfair-ex"]["markets"]["101"]
    except KeyError:
        print(match, "| missing a bookmaker or the 101 market")
        continue
    pin = pinnacle_fair(pin_market)
    bf, backs, lays = betfair_fair(bf_market)
    changed = pin_market["outcomes"]["101"]["players"]["0"]["changedAt"]
    for name in OUTCOMES:
        rows.append([fetched, fx["fixtureId"], fx["startTime"], match, name, 
                     round(pin[name], 4), round(bf[name], 4), 
                     backs[name], lays[name], changed])
    print(match, "| ok")

filename = "benchmark_snapshots.csv"
file_exists = os.path.exists(filename)
with open(filename, "a", newline="") as f:
    writer = csv.writer(f)
    if not file_exists:
        writer.writerow(["snapshot_utc", "fixture_id", "start_time", "match", "outcome", 
                         "pinnacle_fair", "betfair_fair", "betfair_back", "betfair_lay", 
                         "pinnacle_changed_at"])
    writer.writerows(rows)

print(len(rows), "rows saved to", filename)