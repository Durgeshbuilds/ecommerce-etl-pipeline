import os
from dotenv import load_dotenv
import psycopg2
import pandas as pd
import math
from psycopg2.extras import execute_values

from extract import extract
from transform import transform_customers, transform_products, transform_sellers, transform_fact_orders

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "ecommerce_etl"),
    "user": os.getenv("DB_USER", "durgesh"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)



def clean_record(record):
    return tuple(
        None if isinstance(value, float) and math.isnan(value) else value
        for value in record
    )

def load_dim_customers(conn, df):
    with conn.cursor() as cur:
        records = df.to_records(index=False).tolist()
        query = """
            INSERT INTO dim_customers (customer_id, customer_city, customer_state)
            VALUES %s
            ON CONFLICT (customer_id) DO NOTHING
        """
        execute_values(cur, query, records)
    conn.commit()
    print(f"Loaded {len(records)} rows into dim_customers")

def load_dim_products(conn, df):
    with conn.cursor() as cur:
        records = df.to_records(index=False).tolist()
        query = """
            INSERT INTO dim_products (product_id, category, weight_g, length_cm, height_cm, width_cm)
            VALUES %s
            ON CONFLICT (product_id) DO NOTHING
        """
        execute_values(cur, query, records)
    conn.commit()
    print(f"Loaded {len(records)} rows into dim_products")

def load_dim_sellers(conn, df):
    with conn.cursor() as cur:
        records = df.to_records(index=False).tolist()
        query = """
            INSERT INTO dim_sellers (seller_id, seller_city, seller_state)
            VALUES %s
            ON CONFLICT (seller_id) DO NOTHING
        """
        execute_values(cur, query, records)
    conn.commit()
    print(f"Loaded {len(records)} rows into dim_sellers")

def load_fact_orders(conn, df):
    with conn.cursor() as cur:
        df = df.where(pd.notnull(df), None)
        records = df[[
            "order_id", "customer_id", "product_id", "seller_id",
            "purchase_ts", "delivered_ts", "price", "freight_value",
            "payment_value", "review_score"
        ]].to_records(index=False).tolist()
        records = [clean_record(r) for r in records]

        query = """
            INSERT INTO fact_orders (
                order_id, customer_id, product_id, seller_id,
                purchase_ts, delivered_ts, price, freight_value,
                payment_value, review_score
            )
            VALUES %s
        """
        execute_values(cur, query, records)
    conn.commit()
    print(f"Loaded {len(records)} rows into fact_orders")

    
def clear_fact_orders(conn):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE fact_orders;")
    conn.commit()
    print("Cleared fact_orders table")

if __name__ == "__main__":
    dataframes = extract()

    customers = transform_customers(dataframes["olist_customers_dataset"])
    products = transform_products(
        dataframes["olist_products_dataset"],
        dataframes["product_category_name_translation"]
    )
    sellers = transform_sellers(dataframes["olist_sellers_dataset"])
    fact_orders = transform_fact_orders(
        dataframes["olist_orders_dataset"],
        dataframes["olist_order_items_dataset"],
        dataframes["olist_order_payments_dataset"],
        dataframes["olist_order_reviews_dataset"],
    )

    conn = get_connection()
    load_dim_customers(conn, customers)
    load_dim_products(conn, products)
    load_dim_sellers(conn, sellers)
    load_fact_orders(conn, fact_orders)
    conn.close()