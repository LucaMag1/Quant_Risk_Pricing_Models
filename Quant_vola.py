import yfinance as yf

data = yf.download("SPY", start="2020-01-01")

print(data.head())

#Daily returns percentage change

data["Return"] = data["Close"].pct_change()
print(data[["Close", "Return"]].head())

import pandas as pd

data["volatility_20d"] = data["Return"].rolling(window=20).std()
data["volatility_20d_pct"] = data["volatility_20d"] * 100
print(data[["Return", "volatility_20d_pct"]].tail())

#define market shock days
#shock = worst 1% return days
#A shock day is any day where SPY falls more than the threshold. the number of shocks is counted over the full data set, wejust printed the last 5 rows.
#First, we downloaded daily S&P 500 (SPY) closing prices from 2020 onwards. Then we calculated the daily return, which
# is the percentage change in price from one day to the next. After that, we estimated volatility by taking the standard
# deviation of those daily returns over a rolling 20-day window, which tells us how much the daily returns typically
# fluctuate up and down. Finally, we defined “shock days” as the worst 1% of return days, meaning unusually large
# negative moves, so we can study how volatility behaves before and after these extreme events.
threshold = data["Return"].quantile(0.01)
data["shock"] = data["Return"] < threshold  #inferieur a, donc looking only at big drops
print(f"Shock threshold: {threshold*100:.2f}%")
print("Number of shock days:", data["shock"].sum())
print("Max volatility (%):", data["volatility_20d"].max() * 100)
print("Average volatility (%):", data["volatility_20d"].mean() * 100)

#step 4: does volatility stay high after shockdays

#volatility the next day
data["vol_after_shock"] = data["volatility_20d"].shift(-1)

#compare average volatility after shock vs normal days
result = data.groupby("shock")["vol_after_shock"].mean()*100
print("average next daily volatility (%)")
print(result)
#false : normal day
#true : shock day
#Step 4 shows that volatility the next day is about 3× higher after shock days than after normal days, which is evidence of volatility clustering.

# Step 5: Does volatility stay high after shocks?

# Look at volatility 2, 5, and 10 days after a shock
for days in [2, 5, 10]:

    # Volatility "days" after the shock day
    data[f"vol_after_{days}d"] = data["volatility_20d"].shift(-days)

    # Compare average volatility after shock vs normal days
    result = data.groupby("shock")[f"vol_after_{days}d"].mean() * 100

    print(f"\nAverage volatility {days} days later (%):")
    print(result)

# --- Step: keep only isolated shocks (no other shock within ±10 days) ---

window = 10

shock_indices = data.index[data["shock"] == True]

isolated = []

for i in range(len(shock_indices)):
    current = shock_indices[i]

    # shocks within ±10 days
    nearby = shock_indices[
        (shock_indices >= current - pd.Timedelta(days=window*2)) &
        (shock_indices <= current + pd.Timedelta(days=window*2))
    ]

    # isolated means only itself is in that range
    if len(nearby) == 1:
        isolated.append(current)

# create new column
data["isolated_shock"] = data.index.isin(isolated)

print("Number of isolated shocks:", data["isolated_shock"].sum())

#plot
import matplotlib.pyplot as plt

# Plot volatility over time
data["volatility_20d"] = data["Return"].rolling(window=20).std() * 100

plt.figure(figsize=(12,6))
plt.plot(data.index, data["volatility_20d"], label="20-day Volatility (%)")

# Highlight shock days
shock_days = data[data["isolated_shock"] == True]
plt.scatter(shock_days.index, shock_days["volatility_20d"], label="Isolated shock days", marker="x")

plt.title("SPY Volatility Over Time with Shock Days Highlighted")
plt.xlabel("Date")
plt.ylabel("Volatility (%)")
plt.legend()
plt.show()