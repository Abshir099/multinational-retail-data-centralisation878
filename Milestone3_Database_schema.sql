--Milestone 3

--Cast orders_table columns to correct data types
ALTER TABLE orders_table 
ALTER COLUMN date_uuid SET DATA TYPE UUID USING date_uuid::UUID, 
ALTER COLUMN user_uuid SET DATA TYPE UUID USING user_uuid::UUID,
ALTER COLUMN card_number TYPE VARCHAR(19) USING card_number::VARCHAR(19),
ALTER COLUMN store_code TYPE VARCHAR(12) USING store_code::VARCHAR(12),
ALTER COLUMN product_code TYPE VARCHAR(11) USING product_code::VARCHAR(11),
ALTER COLUMN product_quantity TYPE SMALLINT USING product_quantity::SMALLINT;

--Cast dim_users columns to correct data types
ALTER TABLE dim_users
ALTER COLUMN first_name TYPE VARCHAR(255) USING first_name::VARCHAR(255)
ALTER COLUMN last_name TYPE VARCHAR(255) USING last_name::VARCHAR(255),
ALTER COLUMN date_of_birth TYPE DATE USING date_of_birth::DATE,
ALTER COLUMN country_code TYPE VARCHAR(3) USING country_code::VARCHAR(3),
ALTER COLUMN user_uuid TYPE UUID USING user_uuid::uuid,
ALTER COLUMN join_date TYPE DATE USING join_date::DATE,

--update dim_store_details table
ALTER TABLE dim_store_details
ALTER COLUMN longitude TYPE NUMERIC USING longitude::NUMERIC
ALTER COLUMN latitude TYPE NUMERIC USING latitude::NUMERIC,
ALTER COLUMN locality TYPE VARCHAR(255) USING locality::VARCHAR(255),
ALTER COLUMN store_code TYPE VARCHAR(12) USING store_code::VARCHAR(12),
ALTER COLUMN staff_numbers TYPE SMALLINT USING staff_numbers::SMALLINT,
ALTER COLUMN opening_date TYPE DATE USING opening_date::DATE,
ALTER COLUMN store_type TYPE VARCHAR(255) USING store_type::VARCHAR(255),
ALTER COLUMN country_code TYPE VARCHAR(10) USING country_code::VARCHAR(10),
ALTER COLUMN continent TYPE VARCHAR(255) USING continent::VARCHAR(255);

--Make changes to dim_products for delivery team
UPDATE dim_products SET product_price = REPLACE(product_price, '£', '');
ALTER TABLE dim_products
RENAME COLUMN removed TO still_available;
ADD COLUMN weight_class VARCHAR(255);

UPDATE dim_products
SET weight_class = 
    CASE
        WHEN weight::FLOAT < 2 THEN 'Light'
        WHEN weight::FLOAT >= 2 AND weight::FLOAT < 40 THEN 'Mid_Sized'
        WHEN weight::FLOAT >= 40 AND weight::FLOAT < 140 THEN 'Heavy'
        WHEN weight::FLOAT >= 140 THEN 'Truck_Required'
    END;
--update dim_products table with required data types
ALTER TABLE dim_products
ALTER COLUMN weight_class TYPE VARCHAR(14) USING weight_class::VARCHAR(14)
ALTER COLUMN product_price TYPE NUMERIC USING product_price::NUMERIC,
ALTER COLUMN weight TYPE NUMERIC USING weight::NUMERIC,
ALTER COLUMN "EAN" TYPE VARCHAR(3),
ALTER COLUMN product_code TYPE VARCHAR(11) USING product_code::VARCHAR(11),
ALTER COLUMN date_added TYPE DATE USING date_added::DATE,
ALTER COLUMN uuid TYPE UUID USING uuid::uuid,
ALTER COLUMN still_available TYPE BOOL
  USING CASE
    WHEN still_available = 'Removed' THEN FALSE
    ELSE TRUE
  END;

--update dim_date_times table
ALTER TABLE dim_date_times
ALTER COLUMN month TYPE VARCHAR(10) USING month::VARCHAR(10)
ALTER COLUMN year TYPE VARCHAR(10) USING year::VARCHAR(10),
ALTER COLUMN day TYPE VARCHAR(10) USING day::VARCHAR(10),
ALTER COLUMN time_period TYPE VARCHAR(10) USING time_period::VARCHAR(10);

--update dim_card_details
ALTER TABLE dim_card_details
ALTER COLUMN card_number TYPE VARCHAR(22) USING card_number::VARCHAR(22),
ALTER COLUMN expiry_date TYPE VARCHAR(5) USING expiry_date::VARCHAR(5),
ALTER COLUMN  date_payment_confirmed TYPE DATE USING  date_payment_confirmed::DATE;


--Primary keys
--Create the primary keys in the dimension tables
ALTER TABLE dim_users
ADD PRIMARY KEY (user_uuid);

ALTER TABLE dim_store_details
ADD PRIMARY KEY (store_code);

ALTER TABLE dim_products
ADD PRIMARY KEY (product_code);

ALTER TABLE dim_date_times
ADD PRIMARY KEY (date_uuid);

ALTER TABLE dim_card_details
ADD PRIMARY KEY (card_number);




--Foreign keys
--finalising the star_based schema & adding the foreign keys to the orders table
ALTER TABLE orders_table
ADD CONSTRAINT store_code_fkey
FOREIGN KEY (store_code) REFERENCES dim_store_details(store_code),
ADD CONSTRAINT user_uuid_fkey
FOREIGN KEY (user_uuid) REFERENCES dim_users(user_uuid),
ADD CONSTRAINT product_code_fkey
FOREIGN KEY (product_code) REFERENCES dim_products(product_code),
ADD CONSTRAINT date_uuid_fkey
FOREIGN KEY (date_uuid) REFERENCES dim_date_times(date_uuid),
ADD CONSTRAINT card_number_fkey
FOREIGN KEY (card_number) REFERENCES dim_card_details(card_number);
