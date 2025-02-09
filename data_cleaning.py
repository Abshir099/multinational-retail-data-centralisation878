import pandas as pd
from sqlalchemy import inspect
import database_utils
from sqlalchemy import engine
import DataExtractor
import numpy as np
import re
from database_utils import DatabaseConnector

class DataCleaning():
    @staticmethod
    def clean_user_data(engine):
      user_data_to_clean = extractor.read_rds_table(engine,'legacy_users')
      user_data_to_clean.replace("NULL",np.nan, inplace = True)
      user_data_to_clean.dropna(inplace = True)
      user_data_to_clean["join_date"] = pd.to_datetime(user_data_to_clean["join_date"], errors="coerce")
      user_data_to_clean.dropna(subset = ["join_date"], inplace=True)
      user_data_to_clean.dropna(inplace=True)
      cleaned_user_data = user_data_to_clean 
      #user_data_to_clean.to_csv("raw_user_data.csv", index=False)
      return cleaned_user_data
     

# Exporting raw card data

    @staticmethod
    def clean_card_data(link):
        card_data_to_clean = extractor.retrieve_pdf_data(link)
        card_data_to_clean.replace("NULL", np.nan, inplace = True)
        card_data_to_clean.dropna(inplace = True)
        card_data_to_clean.drop_duplicates(subset = "card_number", inplace = True)
        card_data_to_clean["card_number"] = pd.to_numeric(card_data_to_clean["card_number"], errors = "coerce") 
        card_data_to_clean.dropna(subset = ["card_number"], inplace = True)
        card_data_to_clean["date_payment_confirmed"] = pd.to_datetime(card_data_to_clean["date_payment_confirmed"], errors="coerce")
        card_data_to_clean.dropna(subset=["date_payment_confirmed"], inplace=True)
        cleaned_card_data = card_data_to_clean
        #card_data_to_clean.to_csv("raw_card_data.csv", index=False)
        #print("CSV file saved!")
        return cleaned_card_data
    
    @staticmethod 
    def clean_store_data(return_stores_endpoint, headers, num_stores):
       raw_store_data = extractor.retrieve_stores_data(return_stores_endpoint, headers, num_stores)
       #print(type(raw_store_data))
       raw_store_data.replace("NULL", np.nan, inplace = True)
       raw_store_data.dropna(inplace = True)
       raw_store_data["opening_dates"] = pd.to_datetime(raw_store_data["opening_dates"], errors="coerce")
       raw_store_data.dropna(subset=["opening_dates"], inplace=True)
       raw_store_data["staff_number"] = raw_store_data["staff_number"].str.replace(r'[^0-9]', '', regex = True)
       raw_store_data.dropna(subset=["staff_number"], inplace=True)
       cleaned_store_data = raw_store_data
       return cleaned_store_data

#Convert them all to a decimal value representing their weight in kg. Use a 1:1 ratio of ml to g 
# as a rough estimate for the rows containing ml.
#Develop the method to clean up the weight column and remove all excess characters then represent
# the weights as a float.
    @staticmethod
    def convert_product_weights(extracted_s3_data):
       weights_data = extracted_s3_data["weight"]
       weights_kg = []
       for i in weights_data:
          #if it's already a float/int add to new list
          if isinstance(i,(float,int)):
             weights_kg.append(i)
             #cleaning of string values
          elif isinstance(i,(str)):
             searched_values = re.findall(r'\d+\.?\d*', i)
          if searched_values:
             extracted_values = float(searched_values[0])
          if "kg" in i:
             weights_kg.append(f"{extracted_values}kg")
          elif 'g' in i:
             weights_kg.append(f"{extracted_values/1000}kg")
          elif "l" in i:
             weights_kg.append(f"{extracted_values}kg")
          elif 'ml' in i:
             weights_kg.append(f"{extracted_values/1000}kg")
          elif 'lb' in i:
             weights_kg.append(f"{extracted_values * 0.45359237}kg")
          elif 'oz' in i:
             weights_kg.append(f"{extracted_values *  0.0283495}kg")
          else:
             weights_kg.append(np.nan)

          extracted_s3_data['weight'] = weights_kg
          extracted_s3_data.dropna(subset = ['weight'], inplace = True)
          cleaned_product_weights = extracted_s3_data
          return cleaned_product_weights
       

  # Product Details Cleaning Requirements
#- **Change "NULL" strings data type into NULL data type**
#- **Remove NULL values**
#- **Convert all weight into kg units*

    @staticmethod
    def clean_products_data(extracted_s3_data):
       raw_store_weights_data = extractor.convert_product_weights(extracted_s3_data)
       #print(type(raw_store_weights_data))
       raw_store_weights_data = raw_store_weights_data.replace("NULL", np.nan)
       raw_store_weights_data.dropna(inplace = True)
       cleaned_products_data = raw_store_weights_data
       return cleaned_products_data
       


       









engine = database_utils.engine
extractor = DataExtractor.DataExtractor()
db_connector = database_utils.DatabaseConnector()

#f"{DATABASE_TYPE}+{DBAPI}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
#clean user data
cleaned_user_data = DataCleaning.clean_user_data(engine)
#clean card data
link = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf'
cleaned_card_data = DataCleaning.clean_card_data(link)
#clean store data
headers = {"x-api-key":"yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX"}
store_endpoint = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details'
return_stores_endpoint = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/number_stores'
num_stores = 451
cleaned_store_data = DataCleaning.clean_store_data(store_endpoint, headers, num_stores)
#clean
s3_key = 's3://data-handling-public/products.csv'
extracted_s3_data = DataExtractor.DataExtractor.extract_from_s3(s3_key)
cleaned_products_data = DataCleaning.clean_products_data(extracted_s3_data)

#upload clean data to respective tables
db_connector.upload_to_db(cleaned_user_data, 'dim_users', 'sales_data_db.yaml')
db_connector.upload_to_db(cleaned_card_data, 'dim_card_details','sales_data_db.yaml')
db_connector.upload_to_db(cleaned_store_data, 'dim_store_details','sales_data_db.yaml')
db_connector.upload_to_db(cleaned_products_data, 'dim_products', 'sales_data_db.yaml')

#s3
#products_df = pd.DataFrame()