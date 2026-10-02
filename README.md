# Mispricing in sports prediction markets

## Question

Are prices on prediction markets such as Polymarket and Kalshi systematically wrong for soccer and other sports, and can media attention or large bets explain when they move away from fair value?

A market price is a probability. To test whether it is wrong, I need a benchmark for the true probability. I use Pinnacle closing odds, a sharp bookmaker line, after removing the bookmaker's margin.

## Status

Phase 1 is complete: testing whether the benchmark itself is reliable. Phase 2 is in progress: collecting live Polymarket and benchmark snapshots for upcoming Premier League matches. No comparison result has been reported yet.

## What Phase 1 does

1. Loads three Premier League seasons (2023/24 to 2025/26) from football-data.co.uk.
2. Converts Pinnacle closing odds into fair probabilities: take 1 / odds for home, draw and away, then divide each by their sum so they total 100%. This removes the bookmaker's margin (proportional normalization).
3. Pools every outcome (three per match) and groups them by claimed probability in bins of width 0.1.
4. Compares the average claimed probability in each bin with how often the outcome actually happened, with two-standard-error bars.

## Result

Sample: 970 matches (2,910 outcomes), 11 August 2023 to 8 January 2026.

![Calibration chart](results/calibration.png)

Pinnacle's closing probabilities matched actual frequencies closely across the range, and every gap was within two standard errors of zero. Low-probability outcomes happened slightly less often than claimed and high-probability outcomes slightly more often, which is the direction of the favorite-longshot bias, but the differences are inside the noise at this sample size.

| Claimed probability | Outcomes | Avg. claimed | Actual | Gap | Std. error |
|---|---:|---:|---:|---:|---:|
| 0.0 to 0.1 | 118 | 0.072 | 0.059 | 0.013 | 0.024 |
| 0.1 to 0.2 | 510 | 0.157 | 0.143 | 0.014 | 0.016 |
| 0.2 to 0.3 | 1062 | 0.253 | 0.253 | 0.000 | 0.013 |
| 0.3 to 0.4 | 374 | 0.343 | 0.340 | 0.004 | 0.025 |
| 0.4 to 0.5 | 301 | 0.447 | 0.458 | -0.012 | 0.029 |
| 0.5 to 0.6 | 243 | 0.552 | 0.551 | 0.000 | 0.032 |
| 0.6 to 0.7 | 144 | 0.648 | 0.639 | 0.009 | 0.040 |
| 0.7 to 0.8 | 113 | 0.744 | 0.788 | -0.043 | 0.041 |
| 0.8 to 0.9 | 42 | 0.835 | 0.905 | -0.070 | 0.057 |
| 0.9 to 1.0 | 3 | 0.907 | 1.000 | -0.093 | 0.168 |

Gap = average claimed minus actual. Std. error = the random variation expected in the actual rate for that many outcomes. The 0.9 to 1.0 row holds only 3 outcomes and carries no weight.

## Data note

The Pinnacle closing odds columns are empty for 170 matches in 2025/26, from 17 January 2026 to the end of the season, so those matches are excluded. The cause is not confirmed.

## Limitations

- 970 matches cannot detect small biases.
- Bins near 0 and 1 contain few outcomes, and the simple standard error formula is unreliable there.
- Proportional normalization is the simplest way to remove the margin. Other methods (power, Shin) treat longshots differently and could change results where the favorite-longshot bias would appear.
- Premier League only.

## Phase 2: live snapshots (in progress)

- `fetch_epl.py` pulls upcoming Premier League match-winner markets from the Polymarket Gamma API and appends mid, bid, ask, normalized fair value and volume to `polymarket_snapshots.csv`.
- `snapshot_benchmark.py` pulls Pinnacle and Betfair Exchange match-result odds through the OddsPapi API for matches inside a rolling window (`DAYS_AHEAD`) and appends fair probabilities to `benchmark_snapshots.csv`. For Betfair, fair value is the midpoint of the implied probabilities at the best back and best lay price, then normalized.
- `match_fixtures.py` pairs Polymarket matches with OddsPapi fixtures by kickoff time and cleaned team names.

Findings so far:

- Polymarket match-winner markets trade thinly and have a spread of about 1 cent. The comparison therefore uses bid and ask, not the midpoint.
- On the OddsPapi free tier, Pinnacle prices for a match more than a week away did not update between two fetches 25 hours apart, while Betfair prices did. Betfair Exchange is the live benchmark for now. This has not been retested close to kickoff.
- A first one-match comparison used snapshots from different runs, so it is only a sanity check.
- Polymarket and Kalshi fees are not yet included.

## Plan

1. Pull live Polymarket and Kalshi prices for soccer markets (partly done).
2. Log market price against the benchmark probability over weeks.
3. Run the same calibration test on the prediction market data.
4. Test whether news attention and large trades move prices away from fair value, and whether they revert.
5. Build an independent probability model (Elo or Poisson) and test out of sample.
6. Simulate trading with fees and spreads, then paper trade.

Pinnacle closed its public API in July 2025, so the live benchmark for later phases needs another source, such as Betfair Exchange prices.

## How to run

```
pip install -r requirements.txt
```

Create a `data/` folder and download the Premier League CSVs for 2023/24, 2024/25 and 2025/26 from football-data.co.uk, saving them as `pldata2324.csv`, `pldata2425.csv` and `pldata2526.csv`. Then:

```
python probability.py
```

This prints the calibration table and saves the chart to `results/calibration.png`.

For Phase 2, get a free OddsPapi key and store it in an environment variable. The scripts read it with `os.environ`, so the key never appears in the code. Do not commit it.

export ODDSPAPI_KEY="your-key"

python fetch_epl.py
python snapshot_benchmark.py

Each run appends rows to its CSV file, so repeated runs build a time series.

## Structure

```
data/                     raw CSVs (not included)
results/                  output charts
benchmark_snapshots.csv   snapshot of the games
fetch_epl.py              fetching Premier League games
probability.py            data loading, margin removal, calibration table, chart
snapshot_benchmark.py     creating the snapshot of the games using pinnacle, betfair-ex
requirements.txt          requirements
```

## Disclaimer

This is a research project. Nothing here is financial advice, and no strategy has been shown to be profitable.