import pandas as pd 
import os

RAW_DATA_DIR = "raw-data"

files = [
    "olist_customers_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_products_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_geolocation_dataset.csv",
    "product_category_name_translation.csv",
]

def extract():
    dataframes = {}
    for file in files:
        path = os.path.join(RAW_DATA_DIR, file)
        df = pd.read_csv(path)
        # Use filename (without extension) as the key
        key = file.replace(".csv", "")
        dataframes[key] = df
        # print(f"\n--- {key} ---")
        # print(df.info())
    return dataframes

if __name__ == "__main__":
    extract()
