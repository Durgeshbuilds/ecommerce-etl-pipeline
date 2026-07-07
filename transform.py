from extract import extract
import pandas as pd 

def transform_customers(df):
    df = df[["customer_id", "customer_city", "customer_state"]].copy()
    df = df.drop_duplicates(subset="customer_id")
    return df

def transform_products(df, category_translation):
    df = df[["product_id", "product_category_name",
              "product_weight_g", "product_length_cm",
              "product_height_cm", "product_width_cm"]].copy()

    # Merge in English category names
    df = df.merge(category_translation, on="product_category_name", how="left")

    df = df.rename(columns={
        "product_category_name_english": "category",
        "product_weight_g": "weight_g",
        "product_length_cm": "length_cm",
        "product_height_cm": "height_cm",
        "product_width_cm": "width_cm",
    })

    df = df[["product_id", "category", "weight_g", "length_cm", "height_cm", "width_cm"]]
    df = df.drop_duplicates(subset="product_id")
    return df

def transform_sellers(df):
    df = df[["seller_id", "seller_city", "seller_state"]].copy()
    df = df.drop_duplicates(subset="seller_id")
    return df


def transform_fact_orders(orders, order_items, payments, reviews):
    # Aggregate payments: an order can have multiple payment rows (e.g. split payment)
    payments_agg = payments.groupby("order_id")["payment_value"].sum().reset_index()

    # Reviews: one order can technically have >1 review, keep the latest one
    reviews_dedup = reviews.sort_values("review_answer_timestamp").drop_duplicates(
        subset="order_id", keep="last"
    )[["order_id", "review_score"]]

    # Start from order_items (this defines our grain: one row per order item)
    df = order_items[["order_id", "order_item_id", "product_id", "seller_id", "price", "freight_value"]].copy()

    # Bring in customer_id and timestamps from orders
    df = df.merge(
        orders[["order_id", "customer_id", "order_purchase_timestamp", "order_delivered_customer_date"]],
        on="order_id", how="left"
    )

    # Bring in aggregated payment value
    df = df.merge(payments_agg, on="order_id", how="left")

    # Bring in review score
    df = df.merge(reviews_dedup, on="order_id", how="left")

    # Rename to match our schema
    df = df.rename(columns={
        "order_purchase_timestamp": "purchase_ts",
        "order_delivered_customer_date": "delivered_ts",
    })

    # Convert timestamp strings to actual datetime objects
    df["purchase_ts"] = pd.to_datetime(df["purchase_ts"])
    df["delivered_ts"] = pd.to_datetime(df["delivered_ts"])

    return df

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

    print(fact_orders.head())
    print(f"\nfact_orders row count: {len(fact_orders)}")
    print(fact_orders.dtypes)