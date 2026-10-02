import os
import csv
import requests

key = os.environ["ODDSPAPI_KEY"]
url = "https://api.oddspapi.io/v4/fixtures"
params = {"apiKey": key, "tournamentId": 17, "statusId": 0,
          "hasOdds": "true", "bookmakers": "pinnacle"}
fixtures = requests.get(url, params=params, timeout=10).json()

def clean(name):
    words = name.lower().replace("&", "and").split()
    words = [w for w in words if w not in ("fc", "afc")]
    return " ".join(words)

oddspapi = {}
for fx in fixtures:
    k = (fx["startTime"][:16], clean (fx["participant1Name"]), clean(fx["participant2Name"]))
    oddspapi[k] = fx["fixtureId"]

seen = set()
with open("polymarket_snapshots.csv") as f:
    for row in csv.DictReader(f):
        home, away = row["match"].split(" vs. ")
        k = (row["end_date"][:16], clean(home), clean(away))
        if k in seen:
            continue
        seen.add(k)
        print(row["match"], "->", oddspapi.get(k, "NO MATCH"))
