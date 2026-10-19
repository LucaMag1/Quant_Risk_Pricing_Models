
import pandas as pd
from pathlib import Path
# =====================================
# 1. IMPORT DATA
# =====================================

data_file = Path(__file__).resolve().parent / "data" / "prices.csv"
df = pd.read_csv(data_file)

df.rename(columns={df.columns[0]: "Date"}, inplace=True)
df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True)
df.set_index("Date", inplace=True)

df = df.apply(pd.to_numeric, errors="coerce")
df = df.sort_index()
df = df.dropna(how="all")
df = df.dropna(axis=1, how="all")

# Use the latest available data
df = df.loc[:"2026-10-06"]

# Remove invalid prices
df = df.where(df > 0)

# Fill short gaps in price history
df = df.ffill(limit=3)

# Keep actual trading dates with sufficient coverage
df = df.loc[df.notna().sum(axis=1) >= 50]

print("Latest date:", df.index[-1].date())


# =====================================
# 2. CALCULATE MOMENTUM
# =====================================

periods = {
    "1 Week": 5,
    "1 Month": 21,
    "3 Months": 63
}

momentum = pd.DataFrame(index=df.columns)

for name, days in periods.items():

    # Percentage price change
    momentum[name] = (
        df.iloc[-1] / df.iloc[-days-1] - 1
    ) * 100


# =====================================
# 3. FILTER UNRELIABLE STOCKS
# =====================================

# Require valid prices across all three periods
momentum = momentum.dropna()

# Require at least 50 valid observations
valid = df.notna().sum() >= 50
momentum = momentum.loc[momentum.index.intersection(valid[valid].index)]

# Exclude extreme daily price movements
daily_returns = df.pct_change(fill_method=None)

extreme = daily_returns.abs().gt(0.50).any()
momentum = momentum.loc[
    ~extreme.reindex(momentum.index).fillna(False)
]


# =====================================
# 4. RANK STOCKS
# =====================================

# Rank stocks for each period
ranks = momentum.rank(ascending=False)

# Average rank across three periods
momentum["Average Rank"] = ranks.mean(axis=1)

# Select 7 strongest overall candidates
top_20 = momentum.sort_values("Average Rank").head(20)

print("\nTOP 20 STOCKS FOR OCTOBER")
print(top_20.round(2).to_string())

# 4B. VOLATILITY-ADJUSTED MOMENTUM

# Calculate daily returns
daily_returns = df.pct_change(fill_method=None)

# Annualised volatility over the last 63 trading days
volatility = daily_returns.tail(63).std() * (252 ** 0.5)

# Add volatility to the ranking table
momentum["Volatility"] = volatility * 100

# Adjust 3-month momentum for volatility
momentum["Risk Adjusted Momentum"] = (
    momentum["3 Months"] / momentum["Volatility"]
)
# 4C. MOMENTUM CONSISTENCY

# Daily returns over the last 63 trading days
recent_returns = df.pct_change(fill_method=None).tail(63)

# Percentage of days with positive returns
momentum["Positive Days %"] = (
    (recent_returns > 0).sum() /
    recent_returns.notna().sum() * 100
)

# Rank stocks by consistency
momentum["Consistency Rank"] = (
    momentum["Positive Days %"].rank(ascending=False)
)

# Rank stocks by risk-adjusted momentum
momentum["Risk Adjusted Rank"] = (
    momentum["Risk Adjusted Momentum"].rank(ascending=False)
)

# Combine all three rankings
momentum["Final Rank"] = (
    momentum["Average Rank"] +
    momentum["Risk Adjusted Rank"] +
    momentum["Consistency Rank"]
) / 3
# Select the best 20 stocks
top_20 = momentum.sort_values("Final Rank").head(20)

print("\nTOP 20 STOCKS - MOMENTUM + VOLATILITY")
print(top_20.round(2).to_string())
# Show the top 15 with the new information
print("\nTOP 15 WITH RISK-ADJUSTED MOMENTUM")
print(
    momentum.loc[top_20.index][
        ["1 Week", "1 Month", "3 Months",
         "Average Rank", "Volatility", "Risk Adjusted Momentum"]
    ].round(2)
)
# =====================================
# 5. SHOW TOP 10 FOR EACH PERIOD
# =====================================

for name in periods:

    print(f"\nTOP 10 - {name}")
    print(
        momentum[name]
        .sort_values(ascending=False)
        .head(10)
        .round(2)
        .to_string()
    )


# =====================================
# 6. SAVE RESULTS TO CSV
# =====================================

output_file = Path(__file__).resolve().parent / "momentum_top20.csv"

top_20.to_csv(output_file, index=False)

print(f"\nResults saved to: {output_file}")


# =====================================
# 7. PLOT TOP 7 STOCKS
# =====================================

import matplotlib.pyplot as plt

# Get prices for our selected stocks
stocks = top_20.index

# Use the last 3 months of available prices
prices = df[stocks].tail(63)

# Convert prices into percentage returns
# All stocks start at 0% for comparison
performance = (prices / prices.iloc[0] - 1) * 100

# Plot
plt.figure(figsize=(12, 6))

for stock in stocks:
    plt.plot(performance.index, performance[stock],
             label=stock)

plt.title("Top 7 Momentum Stocks - October 2026")
plt.xlabel("Date")
plt.ylabel("Cumulative Return (%)")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

