import pandas as pd

# 1. Load the dataset
df = pd.read_csv("daily_sales_sample.csv")

# 2. Recover missing portions_sold using unit prep cost when available
# Standard unit prep cost for Luwombo = 135,000 UGX / 18 portions = 7,500 UGX
unit_prep_cost = {
    "Katogo": 2400.0,
    "Luwombo": 7500.0,
    "Pilawo": 4200.0,
}

missing_mask = df["portions_sold"].isna()
for idx in df[missing_mask].index:
    item = df.loc[idx, "item"]
    prep_cost = df.loc[idx, "prep_cost_ugx"]
    waste = df.loc[idx, "waste_portions"]
    est_prepared = round(prep_cost / unit_prep_cost[item])
    df.loc[idx, "portions_sold"] = max(est_prepared - waste, 0)

df["portions_sold"] = df["portions_sold"].astype(int)

# 3. Calculate core metrics per row
df["revenue_ugx"] = df["portions_sold"] * df["unit_price_ugx"]
df["gross_profit_ugx"] = df["revenue_ugx"] - df["prep_cost_ugx"]
df["prepared_portions"] = df["portions_sold"] + df["waste_portions"]

# 4. Aggregate by menu item
summary = (
    df.groupby("item", as_index=False)
    .agg(
        portions_sold=("portions_sold", "sum"),
        revenue_ugx=("revenue_ugx", "sum"),
        prep_cost_ugx=("prep_cost_ugx", "sum"),
        gross_profit_ugx=("gross_profit_ugx", "sum"),
        waste_portions=("waste_portions", "sum"),
        prepared_portions=("prepared_portions", "sum"),
    )
)

summary["gross_margin_pct"] = (
    summary["gross_profit_ugx"] / summary["revenue_ugx"] * 100
).round(1)
summary["waste_rate_pct"] = (
    summary["waste_portions"] / summary["prepared_portions"] * 100
).round(1)

print("=== MENU ITEM SUMMARY (CLEANED DATA) ===")
print(
    summary[
        [
            "item",
            "portions_sold",
            "revenue_ugx",
            "prep_cost_ugx",
            "gross_profit_ugx",
            "gross_margin_pct",
            "waste_rate_pct",
        ]
    ].to_string(index=False)
)

print("\n=== WEEKLY TOTALS ===")
total_rev = df["revenue_ugx"].sum()
total_cost = df["prep_cost_ugx"].sum()
total_profit = df["gross_profit_ugx"].sum()
total_waste = df["waste_portions"].sum()
total_prep = df["prepared_portions"].sum()
print(f"Total Portions Sold: {df['portions_sold'].sum()}")
print(f"Total Revenue (UGX): {total_rev:,}")
print(f"Total Prep Cost (UGX): {total_cost:,}")
print(f"Total Gross Profit (UGX): {total_profit:,}")
print(f"Overall Gross Margin: {total_profit / total_rev * 100:.1f}%")
print(f"Overall Waste Rate: {total_waste / total_prep * 100:.1f}%")
