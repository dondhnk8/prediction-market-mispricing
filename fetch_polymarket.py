import requests
import json
from datetime import datetime, timezone

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

params = {
    "limit": 1,
    "end_date_min": now,
    "order": "volume",
    "ascending": "false",
}

response = requests.get("https://gamma-api.polymarket.com/events", params=params)
print(response.url)

events = response.json()
market = events[0]["markets"][0]

outcomes = json.loads(market["outcomes"])
prices = json.loads(market["outcomePrices"])

yes_price = float(prices[0])
no_price = float(prices[1])

print(events[0]["title"])
print(market["question"])
print(market["outcomePrices"])
print(market.get("closed"))
print(market.get("endDate"))
print("Yes probability:", yes_price)
print("No probability:", no_price)
print("Sum:", yes_price + no_price)