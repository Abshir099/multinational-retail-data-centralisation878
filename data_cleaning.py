import pandas as pd
from sqlalchemy import inspect
import database_utils
from sqlalchemy import engine
import DataExtractor
import numpy as np
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
      return cleaned_user_data
    

    @staticmethod
    def clean_card_data(link):
        card_data_to_clean = extractor.retrieve_pdf_data(link)
        card_data_to_clean.replace("NULL", np.nan, inplace = True)
        card_data_to_clean.dropna(inplace = True)
        card_data_to_clean.drop_duplicates(subset = "card_number", inplace = True)
        card_data_to_clean["card_number"] = pd.to_numeric(card_data_to_clean["card_number"], errors = "coerce") 
        card_data_to_clean.dropna(subset = ["card_number"], inplace = True)
        card_data_to_clean["date_payment_confirmed"] = pd.to_datetime(card_data_to_clean["date_payment_confirmed"], errors="coerce", format="mixed")
        card_data_to_clean.dropna(subset=["date_payment_confirmed"], inplace=True)
        cleaned_card_data = card_data_to_clean
        return cleaned_card_data
    
    #def called_clean_store_data():
       


engine = database_utils.engine
extractor = DataExtractor.DataExtractor()
db_connector = database_utils.DatabaseConnector()

#f"{DATABASE_TYPE}+{DBAPI}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
#clean user data
cleaned_user_data = DataCleaning.clean_user_data(engine)
#clean_card_data
link = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf'
cleaned_card_data = DataCleaning.clean_card_data(link)

#upload clean data to respective tables
db_connector.upload_to_db(cleaned_user_data, 'dim_users', 'sales_data_db.yaml')
db_connector.upload_to_db(cleaned_card_data, 'dim_card_details','sales_data_db.yaml')
