-- Dimension: Customers
CREATE TABLE dim_customers (
    customer_id VARCHAR PRIMARY KEY,
    customer_city VARCHAR,
    customer_state VARCHAR
);

-- Dimension: Products
CREATE TABLE dim_products (
    product_id VARCHAR PRIMARY KEY,
    category VARCHAR,
    weight_g NUMERIC,
    length_cm NUMERIC,
    height_cm NUMERIC,
    width_cm NUMERIC
);

-- Dimension: Sellers
CREATE TABLE dim_sellers (
    seller_id VARCHAR PRIMARY KEY,
    seller_city VARCHAR,
    seller_state VARCHAR
);

-- Fact: Order Items (the core transaction table)
CREATE TABLE fact_orders (
    order_item_id SERIAL PRIMARY KEY,
    order_id VARCHAR,
    customer_id VARCHAR REFERENCES dim_customers(customer_id),
    product_id VARCHAR REFERENCES dim_products(product_id),
    seller_id VARCHAR REFERENCES dim_sellers(seller_id),
    purchase_ts TIMESTAMP,
    delivered_ts TIMESTAMP,
    price NUMERIC,
    freight_value NUMERIC,
    payment_value NUMERIC,
    review_score INTEGER
);