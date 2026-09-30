# volatility risk premium: India VIX vs realised Nifty volatility
# question: is VIX (expected vol) usually higher than the vol that actually happens?
# two things used: realised volatility and implied volatility (VIX)
#
# data options:
#   1. yfinance (pip install yfinance), downloads ^NSEI and ^INDIAVIX
#   2. nifty.csv and vix.csv in the same folder with columns Date, Close
#   3. python vrp_study.py --synthetic  -> fake data, only to check the code runs

import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HORIZON = 21      # 30 calendar days is about 21 trading days
START = "2015-01-01"


def load_data():
    if "--synthetic" in sys.argv:
        return synthetic_data()
    try:
        import yfinance as yf
        nifty = yf.download("^NSEI", start=START, progress=False, auto_adjust=True)["Close"].squeeze()
        vix = yf.download("^INDIAVIX", start=START, progress=False, auto_adjust=True)["Close"].squeeze()
    except Exception:
        nifty = pd.read_csv("nifty.csv", parse_dates=["Date"], index_col="Date")["Close"]
        vix = pd.read_csv("vix.csv", parse_dates=["Date"], index_col="Date")["Close"]
    df = pd.concat([nifty.rename("nifty"), vix.rename("vix")], axis=1).dropna()
    return df


def synthetic_data(n=2500, seed=1):
    # fake data just for testing, VIX is made slightly higher than true vol
    rng = np.random.default_rng(seed)
    vol = np.empty(n)
    vol[0] = 0.15
    for i in range(1, n):
        vol[i] = max(0.07, vol[i-1] + 0.05*(0.16 - vol[i-1]) + 0.03*rng.standard_normal()*np.sqrt(1/252))
    ret = 0.0003 + vol/np.sqrt(252) * rng.standard_normal(n)
    price = 10000 * np.exp(np.cumsum(ret))
    vix = 100 * (vol * 1.12 + 0.01 * rng.standard_normal(n))
    idx = pd.bdate_range("2015-01-01", periods=n)
    return pd.DataFrame({"nifty": price, "vix": vix}, index=idx)


def main():
    df = load_data()

    # daily log returns
    df["ret"] = np.log(df["nifty"]).diff()

    # realised vol over the NEXT 21 days, annualised, in percent
    # rolling std looks backward so I shift it back by HORIZON to look forward
    df["realized"] = df["ret"].rolling(HORIZON).std().shift(-HORIZON) * np.sqrt(252) * 100

    df = df.dropna()
    df["premium"] = df["vix"] - df["realized"]

    # numbers
    pct_pos = 100 * (df["premium"] > 0).mean()
    print(f"Observations           : {len(df)}")
    print(f"Average VIX            : {df['vix'].mean():.2f}")
    print(f"Average realized vol   : {df['realized'].mean():.2f}")
    print(f"Average premium        : {df['premium'].mean():.2f} vol points")
    print(f"Median premium         : {df['premium'].median():.2f}")
    print(f"Premium > 0 on         : {pct_pos:.1f}% of days")
    print(f"Worst premium          : {df['premium'].min():.2f}")
    print("Date of worst premium  :", df["premium"].idxmin().date())
    print(f"5th percentile premium : {df['premium'].quantile(0.05):.2f}")

    # save the numbers in README format so I can copy paste them
    with open("results_for_readme.md", "w") as f:
        f.write(f"- Average VIX: {df['vix'].mean():.2f}\n")
        f.write(f"- Average realised vol: {df['realized'].mean():.2f}\n")
        f.write(f"- Average premium: {df['premium'].mean():.2f} vol points\n")
        f.write(f"- Premium positive on: {pct_pos:.1f}% of days\n")
        f.write(f"- Worst premium: {df['premium'].min():.2f}\n")

    # plots
    fig, ax = plt.subplots(2, 1, figsize=(11, 8), sharex=True)

    ax[0].plot(df.index, df["vix"], label="VIX (implied)", lw=1)
    ax[0].plot(df.index, df["realized"], label="Realized vol (next 21 days)", lw=1)
    ax[0].set_ylabel("Volatility (%)")
    ax[0].set_title("Implied vs realized volatility")
    ax[0].legend()

    ax[1].fill_between(df.index, df["premium"], 0, where=df["premium"] >= 0, alpha=0.6, label="Premium > 0")
    ax[1].fill_between(df.index, df["premium"], 0, where=df["premium"] < 0, alpha=0.6, label="Premium < 0")
    ax[1].set_ylabel("VIX - realized")
    ax[1].set_title("Volatility risk premium")
    ax[1].legend()

    plt.tight_layout()
    plt.savefig("vrp_results.png", dpi=150)
    print("\nSaved vrp_results.png")


if __name__ == "__main__":
    main()
