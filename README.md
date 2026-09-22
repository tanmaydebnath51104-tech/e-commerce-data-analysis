# E-Commerce Data Analytics

A self-contained Python data-analytics project that processes the
**E Commerce Dataset.csv** and produces charts, summaries, and
business recommendations.

---

## Project Structure

```
IBM BOB Project/
├── E Commerce Dataset.csv          ← raw data (place here)
└── ecommerce_analytics/
    ├── ecommerce_analysis.py       ← main analysis script
    ├── requirements.txt
    ├── README.md
    ├── category_summary.csv        ← generated output
    └── charts/
        ├── 01_sales_by_category.png
        ├── 02_transactions_by_category.png
        ├── 03_revenue_share_pie.png
        ├── 04_monthly_revenue_trend.png
        ├── 05_payment_method_analysis.png
        ├── 06_avg_discount_by_category.png
        ├── 07_orders_by_day.png
        ├── 08_quarterly_summary.png
        └── 09_sales_distribution.png
```

---

## Dataset Columns

| Column | Description |
|---|---|
| `User_ID` | Unique customer identifier |
| `Product_ID` | Unique product identifier |
| `Category` | Product category (Books, Clothing, …) |
| `Price (Rs.)` | Original price before discount |
| `Discount (%)` | Percentage discount applied |
| `Final_Price(Rs.)` | Price paid after discount |
| `Payment_Method` | Payment channel used |
| `Purchase_Date` | Date of purchase (DD-MM-YYYY) |

> **Sales derivation:** Because every row represents one transaction
> (Quantity = 1), **Sales = Quantity × Final_Price = Final_Price**.
> The `Discount_Amount = Price − Final_Price` is also computed.

---

## Six Analytics Steps

| # | Step | What happens |
|---|---|---|
| 1 | **Load** | Read CSV with `pandas.read_csv` |
| 2 | **Clean** | Drop empty rows, fill missing text, coerce numerics, remove negative prices, parse dates |
| 3 | **Sales metric** | `Sales = Quantity × Final_Price`; `Discount_Amount = Price − Final_Price` |
| 4 | **Summarise** | Group by Category, Payment Method, Month, Quarter, Day-of-Week; compute totals, counts, averages |
| 5 | **Charts** | 9 charts saved to `charts/` |
| 6 | **Insights** | 9 business recommendations printed to the console |

---

## Setup & Run

```bash
# 1 – install dependencies (once)
pip install -r ecommerce_analytics/requirements.txt

# 2 – run from the project root
python ecommerce_analytics/ecommerce_analysis.py
```

---

## Charts Generated

| File | Description |
|---|---|
| `01_sales_by_category.png` | Horizontal bar – total revenue per category |
| `02_transactions_by_category.png` | Vertical bar – order count per category |
| `03_revenue_share_pie.png` | Donut chart – % revenue share by category |
| `04_monthly_revenue_trend.png` | Line chart with fill – monthly revenue trend |
| `05_payment_method_analysis.png` | Dual-axis bar+line – transactions & avg sale by payment method |
| `06_avg_discount_by_category.png` | Bar chart – average discount rate per category |
| `07_orders_by_day.png` | Bar chart – orders by day of the week |
| `08_quarterly_summary.png` | Grouped bar – quarterly revenue & orders |
| `09_sales_distribution.png` | Histogram with mean/median lines |

---

## Sample Business Recommendations

* **Expand the top-revenue category** – increase product range and ad spend.
* **Revive underperforming categories** – targeted promotions or bundling.
* **Reward the preferred payment method** – negotiate lower fees or add cashback.
* **Capitalise on peak months** – pre-stock inventory and schedule flash sales.
* **Protect margins on high-discount categories** – replace discounts with value-add bundles.
* **Loyalty programme for top 10 customers** – they drive disproportionate revenue.
