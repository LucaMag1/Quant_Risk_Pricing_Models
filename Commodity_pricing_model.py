#Task 2 is: use that price function to compute the
# contract value = money from selling − money spent buying − fees.
import pandas as pd
from Commodity_storage import estimate_price

print(estimate_price("2023-06-15"))


from Commodity_storage import estimate_price

def price_storage_contract(
    injection_dates, #list of dates when we buy + inject gas
    withdrawal_dates, #list of dates when we withdraw + sell gas
    rate, #max amount you can inject or withdraw per day
    max_volume, #max gas you can hold in the tank
    storage_cost_per_month=0.0,
    inj_cost_per_unit=0.0, #optional fees per unit moved
    wd_cost_per_unit=0.0,
):

# converting strings into date objects pandas understands
    injection_dates = pd.to_datetime(injection_dates)
    withdrawal_dates = pd.to_datetime(withdrawal_dates)

# find the time window of the contract
    start = min(injection_dates.min(), withdrawal_dates.min()) #earliest date
    end = max(injection_dates.max(), withdrawal_dates.max()) #latest date

    days = pd.date_range(start, end, freq="D") #create every day between start and end

    inj_set = set(injection_dates.date) #turn injection/withdrawal dates into sets so we can quickly ask
    wd_set = set(withdrawal_dates.date)

    #  Simulate inventory + cashflows
    inventory = 0.0
    value = 0.0

    for d in days:
        day = d.date()

        # Inject (buy gas)
        if day in inj_set:
            vol = min(rate, max_volume - inventory)
            inventory += vol
            value -= vol * float(estimate_price(d))
            value -= vol * inj_cost_per_unit

        # Withdraw (sell gas)
        if day in wd_set:
            vol = min(rate, inventory)
            inventory -= vol
            value += vol * float(estimate_price(d))
            value -= vol * wd_cost_per_unit

    # --- 3) Storage cost charged per month over span (inclusive) ---
    n_months = (end.year - start.year) * 12 + (end.month - start.month) + 1
    value -= n_months * storage_cost_per_month

    return float(value)

if __name__ == "__main__":
    # Simple sanity test
    v = price_storage_contract(
        injection_dates=["2023-06-30", "2023-07-14", "2023-08-02", "2023-09-24"],
        withdrawal_dates=["2023-12-28", "2024-01-14", "2024-02-29", "2024-03-31"],
        rate=300_000,
        max_volume=1_000_000,
        storage_cost_per_month=100_000,
    )
    print("Contract value:", v)