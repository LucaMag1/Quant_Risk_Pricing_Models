#building a model that estimates the price of natural gas for any date using historical monthly price data.
#To do that, you clean the data, detect patterns (like seasonality), and create a mathematical function that can interpolate between known dates and extrapolate into the future.
#This estimated price curve will later be used to help value and analyse a gas storage contract.
import pandas as pd

df = pd.read_csv("Nat_Gas.csv")

df["Dates"] = pd.to_datetime(df["Dates"], format="%m/%d/%y")
df = df.sort_values("Dates")
df.set_index("Dates", inplace=True)

print(df.head())


# Quick visual sanity check to see seasonality/trends
import matplotlib.pyplot as plt

plt.plot(df.index, df["Prices"])
plt.title("Natural Gas Monthly Prices")
plt.show()


#Create interpolation model
from scipy.interpolate import interp1d
import numpy as np

       #Convert dates to numeric values : x is dates as numbers and y is prices
x = df.index.map(pd.Timestamp.toordinal)
y = df["Prices"].values
       #interp1d interpolates in 1D, estimates between points. A point: (date1, price1)
       #interp1d needs the coordinates of each point so x and y.
       #kind = linear draws a straight line between two consecutive points to determine a value in the middle.
       #fill value is extrapolate to extend those lines beyond the data to estimate future prices
model = interp1d(x, y, kind = "linear", bounds_error = False)

#monthly seasonality
df["Month"] = df.index.month
monthly_avg = df.groupby("Month")["Prices"].mean()

#pd.todatetime is a built in function in pandas that turns text into a real date object
#toordinal converts date into a number
def estimate_price(date_str):
    d = pd.to_datetime(date_str)

    # If within historical range -> interpolation
    if d >= df.index.min() and d <= df.index.max():
        return float(model(d.toordinal()))

    # If outside (future or earlier) -> seasonal estimate (month-of-year average)
    return float(monthly_avg[d.month])

end_date = df.index.max() + pd.DateOffset(years=1)
dates = pd.date_range(df.index.min(), end_date, freq="D")

x_plot = dates.map(pd.Timestamp.toordinal).astype(float)
y_plot = np.array([estimate_price(dt) for dt in dates], dtype=float)

plt.figure()
plt.plot(df.index, df["Prices"], marker="o", linestyle="-", label="Monthly data")
plt.plot(dates, y_plot, linestyle="--", label="Interpolated/extrapolated curve")
plt.title("Natural Gas Price Estimate (Interpolation + 1Y Extrapolation)")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.show()