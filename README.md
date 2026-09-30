# Volatility Risk Premium: India VIX vs Realised Nifty Volatility

I wanted to check if the market's expected volatility (India VIX) is usually higher than the volatility that actually happens afterwards.

## Why I made this
Options traders earn money from the gap between implied and realised volatility, so I wanted to check this gap on real Indian market data instead of just reading about it. I also wanted a project that uses simple statistics and real data rather than a complicated model.

## What I did
- Took daily log returns of Nifty 50: `r = ln(P_t / P_(t-1))`
- Calculated realised volatility over the next 21 trading days: `std(returns) * sqrt(252) * 100`
- Premium = VIX - realised volatility. If it is positive, people who sold options were paid more than the risk they faced.
- Plotted both series and the premium, and looked at the worst periods

## How to run
```
pip install numpy pandas matplotlib yfinance
python vrp_study.py
```
If yfinance does not work, download Nifty and India VIX data as `nifty.csv` and `vix.csv` (columns `Date, Close`) and keep them in the same folder.

## Results
- Average VIX: 16.59
- Average realised vol: 14.12
- Average premium: 2.46 vol points
- Premium positive on: 79.7% of days
- Worst premium: -64.50 (on 2020-03-05, start of the COVID crash) 

[results](vrp_results.png)

The average premium looks attractive, but one crash period wiped out a large part of it, so selling volatility is risky.

## Limitations
- VIX is a 30 calendar day estimate, and I used 21 trading days as an approximation
- I did not include trading costs
- The average looks good, but option sellers can lose a lot in rare crash periods, so the worst values matter more than the average
