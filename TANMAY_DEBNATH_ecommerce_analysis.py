# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

"""
E-Commerce Data Analytics
=========================
Steps performed:
  1. Load the CSV dataset
  2. Inspect and clean missing / incorrect values
    3. Derive Sales = Quantity × Unit_Price (post-discount unit price)
  4. Group & summarise with totals, counts, and averages
  5. Visualise with charts
  6. Print business-decision insights
"""

import os
import sys
import warnings

import matplotlib
matplotlib.use("Agg")          # headless rendering – no display required
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── paths ──────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
CSV_PATH     = os.path.join(SCRIPT_DIR, "E Commerce Dataset.csv")
CHARTS_DIR   = os.path.join(SCRIPT_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# colour palette
PALETTE = ["#3b82f6", "#f59e0b", "#10b981", "#ef4444",
           "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"]

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 – Load dataset
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("  E-COMMERCE DATA ANALYTICS")
print("=" * 60)

print("\n[STEP 1] Loading dataset …")
try:
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    sys.exit(f"  [ERR]  File not found: {CSV_PATH}")

print(f"  [OK]  Loaded {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"  Columns: {list(df.columns)}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 – Data quality check
# ══════════════════════════════════════════════════════════════════════════════
print("\n[STEP 2] Checking data quality …")

# --- missing values ---
missing = df.isnull().sum()
print("\n  Missing values per column:")
print(missing.to_string(header=False))

# --- drop fully empty rows ---
before = len(df)
df.dropna(how="all", inplace=True)
dropped_rows = before - len(df)
if dropped_rows:
    print(f"\n  Dropped {dropped_rows} fully-empty rows.")

# --- fill remaining NaN in text cols with 'Unknown' ---
text_cols = df.select_dtypes(include="object").columns.tolist()
df[text_cols] = df[text_cols].fillna("Unknown")

# --- numeric columns ---
num_cols = ["Price (Rs.)", "Discount (%)", "Final_Price(Rs.)"]
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# remove rows where any numeric column is negative or zero (data error)
mask_valid = (df["Price (Rs.)"] > 0) & (df["Final_Price(Rs.)"] > 0)
invalid_count = (~mask_valid).sum()
if invalid_count:
    print(f"  Removed {invalid_count} rows with non-positive prices.")
df = df[mask_valid].copy()

# --- parse dates ---
df["Purchase_Date"] = pd.to_datetime(df["Purchase_Date"], format="%d-%m-%Y", errors="coerce")
bad_dates = df["Purchase_Date"].isna().sum()
if bad_dates:
    print(f"  Warning: {bad_dates} rows with unparseable dates.")

df["Month"]        = df["Purchase_Date"].dt.to_period("M").astype(str)
df["Month_Number"] = df["Purchase_Date"].dt.month
df["Quarter"]      = df["Purchase_Date"].dt.quarter.map(lambda q: f"Q{q}")
df["DayOfWeek"]    = df["Purchase_Date"].dt.day_name()

print(f"\n  [OK]  Clean dataset: {df.shape[0]:,} rows")
print(f"  Date range: {df['Purchase_Date'].min().date()} → {df['Purchase_Date'].max().date()}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 – Derive Sales metric
# ══════════════════════════════════════════════════════════════════════════════
print("\n[STEP 3] Calculating Sales …")

# Each row represents one unit sale, so quantity is 1.
# Final_Price(Rs.) is the post-discount price for that unit.
# Discount_Amount      = Price - Final_Price
# Discount_Rate        = Discount (%) already in dataset
df["Quantity"]         = 1
df["Unit_Price"]       = df["Final_Price(Rs.)"]
df["Sales"]            = df["Quantity"] * df["Unit_Price"]
df["Discount_Amount"]  = df["Price (Rs.)"] - df["Final_Price(Rs.)"]

print(f"  Total transactions : {len(df):,}")
print(f"  Total Revenue      : Rs. {df['Sales'].sum():,.2f}")
print(f"  Total Discount     : Rs. {df['Discount_Amount'].sum():,.2f}")
print(f"  Avg Sale Value     : Rs. {df['Sales'].mean():,.2f}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 – Group & Summarise
# ══════════════════════════════════════════════════════════════════════════════
print("\n[STEP 4] Grouping & summarising …")

# ── 4a. Category summary ──
cat_summary = (
    df.groupby("Category")
    .agg(
        Total_Sales    = ("Sales",           "sum"),
        Transactions   = ("Sales",           "count"),
        Avg_Sale       = ("Sales",           "mean"),
        Avg_Discount   = ("Discount (%)",    "mean"),
        Total_Discount = ("Discount_Amount", "sum"),
    )
    .sort_values("Total_Sales", ascending=False)
    .round(2)
)
print("\n  ── Category Summary ──")
print(cat_summary.to_string())

# ── 4b. Payment method summary ──
pay_summary = (
    df.groupby("Payment_Method")
    .agg(
        Total_Sales  = ("Sales", "sum"),
        Transactions = ("Sales", "count"),
        Avg_Sale     = ("Sales", "mean"),
    )
    .sort_values("Transactions", ascending=False)
    .round(2)
)
print("\n  ── Payment Method Summary ──")
print(pay_summary.to_string())

# ── 4c. Monthly revenue trend ──
monthly = (
    df.groupby("Month")
    .agg(Revenue=("Sales", "sum"), Orders=("Sales", "count"))
    .reset_index()
    .sort_values("Month")
    .round(2)
)
print(f"\n  ── Monthly Revenue (first 6 months) ──")
print(monthly.head(6).to_string(index=False))

# ── 4d. Quarterly summary ──
quarterly = (
    df.groupby("Quarter")
    .agg(Revenue=("Sales", "sum"), Orders=("Sales", "count"), Avg_Sale=("Sales", "mean"))
    .reset_index()
    .round(2)
)
print("\n  ── Quarterly Summary ──")
print(quarterly.to_string(index=False))

# ── 4e. Day-of-week pattern ──
dow_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
dow_summary = (
    df.groupby("DayOfWeek")
    .agg(Revenue=("Sales", "sum"), Orders=("Sales", "count"))
    .reindex(dow_order)
    .dropna()
    .round(2)
)
print("\n  ── Day-of-Week Orders ──")
print(dow_summary.to_string())

# ── 4f. Top 10 users by spend ──
top_users = (
    df.groupby("User_ID")
    .agg(Total_Spent=("Sales", "sum"), Orders=("Sales", "count"))
    .sort_values("Total_Spent", ascending=False)
    .head(10)
    .round(2)
)
print("\n  ── Top 10 Customers by Spend ──")
print(top_users.to_string())

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 – Charts
# ══════════════════════════════════════════════════════════════════════════════
print("\n[STEP 5] Generating charts …")

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "#f9fafb",
    "axes.grid":        True,
    "grid.color":       "#e5e7eb",
    "grid.linewidth":   0.7,
    "axes.spines.top":  False,
    "axes.spines.right": False,
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   13,
    "axes.labelsize":   11,
})

# ── Chart 1: Total Sales by Category (horizontal bar) ──
fig, ax = plt.subplots(figsize=(9, 5))
cats   = cat_summary.index.tolist()
values = cat_summary["Total_Sales"].values
colors = PALETTE[:len(cats)]
bars   = ax.barh(cats, values, color=colors, height=0.6)
for bar, val in zip(bars, values):
    ax.text(val + max(values) * 0.005, bar.get_y() + bar.get_height() / 2,
            f"Rs.{val:,.0f}", va="center", fontsize=9)
ax.set_xlabel("Total Revenue (Rs.)")
ax.set_title("Total Sales Revenue by Category")
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rs.{x:,.0f}"))
plt.tight_layout()
path1 = os.path.join(CHARTS_DIR, "01_sales_by_category.png")
plt.savefig(path1, dpi=130, bbox_inches="tight")
plt.close()
print(f"  [OK]  {path1}")

# ── Chart 2: Transaction Count by Category (bar) ──
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(cat_summary.index, cat_summary["Transactions"], color=PALETTE[:len(cat_summary)])
ax.set_ylabel("Number of Transactions")
ax.set_title("Transaction Count by Category")
ax.set_xticklabels(cat_summary.index, rotation=15, ha="right")
for i, v in enumerate(cat_summary["Transactions"]):
    ax.text(i, v + 2, str(v), ha="center", fontsize=9)
plt.tight_layout()
path2 = os.path.join(CHARTS_DIR, "02_transactions_by_category.png")
plt.savefig(path2, dpi=130, bbox_inches="tight")
plt.close()
print(f"  [OK]  {path2}")

# ── Chart 3: Sales Distribution – Pie chart ──
fig, ax = plt.subplots(figsize=(7, 7))
wedge_props = dict(width=0.55, edgecolor="white", linewidth=2)
ax.pie(
    cat_summary["Total_Sales"],
    labels=cat_summary.index,
    autopct="%1.1f%%",
    startangle=140,
    colors=PALETTE[:len(cat_summary)],
    wedgeprops=wedge_props,
    pctdistance=0.75,
)
ax.set_title("Revenue Share by Category (Donut)", pad=20)
plt.tight_layout()
path3 = os.path.join(CHARTS_DIR, "03_revenue_share_pie.png")
plt.savefig(path3, dpi=130, bbox_inches="tight")
plt.close()
print(f"  [OK]  {path3}")

# ── Chart 4: Monthly Revenue Trend (line) ──
fig, ax = plt.subplots(figsize=(12, 5))
x_vals = range(len(monthly))
ax.plot(x_vals, monthly["Revenue"], marker="o", linewidth=2,
        color=PALETTE[0], markerfacecolor="white", markeredgewidth=2)
ax.fill_between(x_vals, monthly["Revenue"], alpha=0.12, color=PALETTE[0])
ax.set_xticks(x_vals)
ax.set_xticklabels(monthly["Month"], rotation=45, ha="right", fontsize=8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rs.{x:,.0f}"))
ax.set_title("Monthly Revenue Trend")
ax.set_ylabel("Revenue (Rs.)")
plt.tight_layout()
path4 = os.path.join(CHARTS_DIR, "04_monthly_revenue_trend.png")
plt.savefig(path4, dpi=130, bbox_inches="tight")
plt.close()
print(f"  [OK]  {path4}")

# ── Chart 5: Payment Method – stacked bar (transactions vs avg sale) ──
fig, ax1 = plt.subplots(figsize=(8, 5))
ax2 = ax1.twinx()
x = np.arange(len(pay_summary))
ax1.bar(x, pay_summary["Transactions"], color=PALETTE[1], alpha=0.8, label="Transactions")
ax2.plot(x, pay_summary["Avg_Sale"], marker="D", color=PALETTE[0],
         linewidth=2, label="Avg Sale (Rs.)", zorder=5)
ax1.set_xticks(x)
ax1.set_xticklabels(pay_summary.index, rotation=10)
ax1.set_ylabel("Number of Transactions", color=PALETTE[1])
ax2.set_ylabel("Average Sale (Rs.)", color=PALETTE[0])
ax1.set_title("Payment Method: Transactions & Average Sale Value")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
plt.tight_layout()
path5 = os.path.join(CHARTS_DIR, "05_payment_method_analysis.png")
plt.savefig(path5, dpi=130, bbox_inches="tight")
plt.close()
print(f"  [OK]  {path5}")

# ── Chart 6: Average Discount % by Category ──
fig, ax = plt.subplots(figsize=(9, 5))
disc_vals = cat_summary["Avg_Discount"].sort_values(ascending=False)
bars = ax.bar(disc_vals.index, disc_vals.values,
              color=[PALETTE[i % len(PALETTE)] for i in range(len(disc_vals))], width=0.55)
for bar, val in zip(bars, disc_vals.values):
    ax.text(bar.get_x() + bar.get_width() / 2, val + 0.3, f"{val:.1f}%",
            ha="center", fontsize=9)
ax.set_ylabel("Average Discount (%)")
ax.set_title("Average Discount Rate by Category")
ax.set_xticklabels(disc_vals.index, rotation=15, ha="right")
plt.tight_layout()
path6 = os.path.join(CHARTS_DIR, "06_avg_discount_by_category.png")
plt.savefig(path6, dpi=130, bbox_inches="tight")
plt.close()
print(f"  [OK]  {path6}")

# ── Chart 7: Day-of-Week Order Frequency ──
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(dow_summary.index, dow_summary["Orders"],
       color=PALETTE[2], alpha=0.85, width=0.6)
ax.set_ylabel("Number of Orders")
ax.set_title("Orders by Day of the Week")
for i, v in enumerate(dow_summary["Orders"]):
    ax.text(i, v + 1, str(v), ha="center", fontsize=9)
plt.tight_layout()
path7 = os.path.join(CHARTS_DIR, "07_orders_by_day.png")
plt.savefig(path7, dpi=130, bbox_inches="tight")
plt.close()
print(f"  [OK]  {path7}")

# ── Chart 8: Quarterly Revenue & Orders (grouped bar) ──
fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(quarterly))
w = 0.35
b1 = ax.bar(x - w/2, quarterly["Revenue"],  width=w, label="Revenue (Rs.)", color=PALETTE[0])
b2 = ax.bar(x + w/2, quarterly["Orders"],   width=w, label="Orders",        color=PALETTE[3])
ax.set_xticks(x)
ax.set_xticklabels(quarterly["Quarter"])
ax.set_title("Quarterly Revenue & Order Count")
ax.legend()
plt.tight_layout()
path8 = os.path.join(CHARTS_DIR, "08_quarterly_summary.png")
plt.savefig(path8, dpi=130, bbox_inches="tight")
plt.close()
print(f"  [OK]  {path8}")

# ── Chart 9: Sales Distribution Histogram ──
fig, ax = plt.subplots(figsize=(9, 5))
ax.hist(df["Sales"], bins=40, color=PALETTE[4], edgecolor="white", linewidth=0.5)
ax.axvline(df["Sales"].mean(),   color=PALETTE[3], linestyle="--", linewidth=1.5, label=f"Mean  Rs.{df['Sales'].mean():.2f}")
ax.axvline(df["Sales"].median(), color=PALETTE[1], linestyle="--", linewidth=1.5, label=f"Median Rs.{df['Sales'].median():.2f}")
ax.set_xlabel("Sale Value (Rs.)")
ax.set_ylabel("Frequency")
ax.set_title("Distribution of Sale Values")
ax.legend()
plt.tight_layout()
path9 = os.path.join(CHARTS_DIR, "09_sales_distribution.png")
plt.savefig(path9, dpi=130, bbox_inches="tight")
plt.close()
print(f"  [OK]  {path9}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 – Business Insights & Decisions
# ══════════════════════════════════════════════════════════════════════════════
print("\n[STEP 6] Business Insights & Recommendations")
print("=" * 60)

top_cat    = cat_summary["Total_Sales"].idxmax()
low_cat    = cat_summary["Total_Sales"].idxmin()
top_pay    = pay_summary["Transactions"].idxmax()
best_month = monthly.loc[monthly["Revenue"].idxmax(), "Month"]
worst_month= monthly.loc[monthly["Revenue"].idxmin(), "Month"]
high_disc  = cat_summary["Avg_Discount"].idxmax()
top_q      = quarterly.loc[quarterly["Revenue"].idxmax(), "Quarter"]
peak_day   = dow_summary["Orders"].idxmax()

insights = [
    ("Revenue Leader",
     f"'{top_cat}' generates the highest revenue "
     f"(Rs. {cat_summary.loc[top_cat,'Total_Sales']:,.2f}). "
     "→ Increase product variety and marketing spend in this category."),

    ("Underperformer",
     f"'{low_cat}' has the lowest revenue. "
     "→ Review pricing, run targeted promotions, or consider bundling with top categories."),

    ("Preferred Payment",
     f"'{top_pay}' is the most-used payment method "
     f"({pay_summary.loc[top_pay,'Transactions']:,} transactions). "
     "→ Negotiate better processing rates and offer exclusive cashback for this method."),

    ("Peak Month",
     f"Highest revenue recorded in {best_month}. "
     "→ Prepare inventory and run flash-sales campaigns before this period."),

    ("Low Month",
     f"Lowest revenue in {worst_month}. "
     "→ Launch off-season discounts or loyalty incentives to boost slow periods."),

    ("Discount Strategy",
     f"'{high_disc}' carries the highest average discount "
     f"({cat_summary.loc[high_disc,'Avg_Discount']:.1f}%). "
     "→ Audit whether deep discounts are protecting margins; consider value-add bundles instead."),

    ("Best Quarter",
     f"{top_q} is the strongest quarter. "
     "→ Align supply chain and staffing to handle Q-peak demand."),

    ("Peak Shopping Day",
     f"Most orders placed on {peak_day}. "
     "→ Schedule email campaigns and push notifications for mid-week days to smooth order flow."),

    ("Revenue Concentration",
     f"Top 10 customers account for "
     f"Rs. {top_users['Total_Spent'].sum():,.2f} in spend. "
     "→ Introduce a VIP loyalty tier to retain these high-value customers."),
]

for i, (title, text) in enumerate(insights, 1):
    print(f"\n  {i}. {title}")
    print(f"     {text}")

# ── Save summary CSV ──
summary_path = os.path.join(SCRIPT_DIR, "category_summary.csv")
cat_summary.to_csv(summary_path)
print(f"\n  [OK]  Category summary saved → {summary_path}")

print("\n" + "=" * 60)
print(f"  All {len(insights)} insights generated. Charts saved in: {CHARTS_DIR}")
print("=" * 60)
