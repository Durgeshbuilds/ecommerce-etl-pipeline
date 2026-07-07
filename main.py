import time
import logging
from extract import extract
from transform import transform_customers, transform_products, transform_sellers, transform_fact_orders

from load import (
    get_connection, load_dim_customers, load_dim_products,
    load_dim_sellers, load_fact_orders, clear_fact_orders
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

def run_pipeline():
    start = time.time()
    logging.info("Pipeline started")

    try:
        dataframes = extract()
        logging.info("Extract complete")

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
        logging.info("Transform complete")

        conn = get_connection()
        load_dim_customers(conn, customers)
        load_dim_products(conn, products)
        load_dim_sellers(conn, sellers)
        clear_fact_orders(conn)
        load_fact_orders(conn, fact_orders)
        conn.close()
        logging.info("Load complete")

        duration = round(time.time() - start, 2)
        logging.info(f"Pipeline finished successfully in {duration}s")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    run_pipeline()