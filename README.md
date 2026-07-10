# E-Commerce ETL Pipeline

A batch ETL pipeline that extracts raw e-commerce transaction data, transforms it into a clean star schema, and loads it into PostgreSQL — built to practice real-world data engineering fundamentals.

## Dataset

[Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — ~100k orders across customers, products, sellers, payments, and reviews.

## Architecture

**Target schema (star schema):**
- `dim_customers` — customer_id, city, state
- `dim_products` — product_id, category, dimensions
- `dim_sellers` — seller_id, city, state
- `fact_orders` — one row per order item, linking all dimensions with price, freight, payment, review score

## Tech Stack

- Python 3.14 (pandas, psycopg2)
- PostgreSQL 17
- Logging with Python's `logging` module

## Setup

1. Clone the repo and create a virtual environment:
```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
```

2. Download the [Olist dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and place the CSVs in a `raw-data/` folder in the project root.

3. Create the database and schema:
```bash
   psql postgres -c "CREATE DATABASE ecommerce_etl;"
   psql -d ecommerce_etl -f schema.sql
```

4. Create a `.env` file:

5. Run the pipeline:
```bash
   python3 main.py
```

## Design Decisions

- **Star schema** — chosen over a normalized schema to optimize for analytical queries (fast joins between one fact table and small dimension tables).
- **Idempotent dimension loads** — `ON CONFLICT DO NOTHING` on dimension tables makes re-running the pipeline safe.
- **Full refresh on fact table** — `fact_orders` is truncated and reloaded on every run for simplicity and correctness. This is a known tradeoff — see Limitations below.
- **NaN handling** — pandas silently converts `None` back to `NaN` in numeric columns due to dtype coercion; this is handled explicitly before inserting into PostgreSQL to avoid type errors.

## Known Limitations & Future Improvements

- No true incremental loading yet — every run does a full reload of `fact_orders`. Next step: track a watermark (e.g. last loaded timestamp) to only load new/changed rows.
- No automated tests yet.
- No orchestration tool (Airflow) — currently runs as a single script, would need scheduling for production use.
- No containerization (Docker) yet.

## What I Learned

Building this surfaced a real pandas/psycopg2 edge case: `df.where(pd.notnull(df), None)` doesn't reliably convert `NaN` to `None` in float columns because pandas re-coerces the column back to its dtype. Fixed by manually sanitizing each record with `math.isnan()` before inserting.

