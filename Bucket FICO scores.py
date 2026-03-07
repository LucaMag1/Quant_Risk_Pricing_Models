import pandas as pd

df = pd.read_excel("Task_3_Loan_Data.xlsx")

# Keep only what Task 4 needs
fico_df = df[["fico_score", "default"]].copy()

# Create 10 FICO buckets with roughly equal numbers of borrowers
fico_df["bucket"] = pd.qcut(fico_df["fico_score"], q=10, duplicates="drop")

# Group by bucket and calculate summary stats
rating_map = fico_df.groupby("bucket").agg(
    borrowers=("default", "count"),
    defaults=("default", "sum"),
    avg_fico=("fico_score", "mean")
)

# Probability of default in each bucket
rating_map["pd"] = rating_map["defaults"] / rating_map["borrowers"]

# Sort from best credit to worst credit (highest average FICO first)
rating_map = rating_map.sort_values("avg_fico", ascending=False).reset_index()

# Create rating numbers: 1 = best credit, 2 = next best, etc.
rating_map["rating"] = range(1, len(rating_map) + 1)

# Reorder columns
rating_map = rating_map[["rating", "bucket", "avg_fico", "borrowers", "defaults", "pd"]]

# Round for readability
rating_map["avg_fico"] = rating_map["avg_fico"].round(2)
rating_map["pd"] = rating_map["pd"].round(4)

print(rating_map)