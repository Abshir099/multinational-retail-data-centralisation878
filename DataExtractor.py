import pandas as pd
from sqlalchemy import inspect
import database_utils
import tabula
import requests

class DataExtractor:
    @staticmethod
    def list_db_tables(engine): ## engine as a parameter as we use it tp later connect to a database
        inspector = inspect(engine) ## we've imported inspect from sqlalchemy, inspect allows to us to create an inspector object, which enables you to explore and retrieve detailed metadata about your database.
        tables = inspector.get_table_names()
        return tables
    @staticmethod    
    def read_rds_table(engine, table_name): ## parameters taken: engine to connect to database and use it's info and table_name that we're going to call on.
        query = (f"SELECT * FROM {table_name}") ## to extract the table containing user data, we use SQL since the it's in sql. Write in sql code and use fstring the code can be reuasble instead of directly entering the table name. this is called dynamic programming
        df = pd.read_sql_query(query,engine)      ##returning a pandas DataFrame by using pd. then have pandas read it in sql format. The two arguments it takes will be query and engone. engine is used to connect it to the database and query to
        return df
    @staticmethod
    def retrieve_pdf_data(link):
        extracted_data = tabula.read_pdf(link, pages = 'all')
        # Combine all tables into a single DataFrame to check if extracted_data is a list
        if isinstance(extracted_data, list):
            return pd.concat(extracted_data, ignore_index=True)
        # then use Use pd.concat() to merge all the DataFrames in the list into a single DataFrame.
        elif isinstance(extracted_data, pd.DataFrame):
            return extracted_data
        else:
            raise ValueError("Error: extracted_data is neither a list nor a valid DataFrame.")
    @staticmethod
    def list_number_of_stores(store_endpoint,headers):
        try:
            response = requests.get(store_endpoint, headers=headers)
            if response.status_code == 200:
                stores_data = response.json()
                return stores_data
            else:
                return f"Error:{response.status_code}:{response.text}"
        except requests.exceptions.RequestException as e:
            print(f"Error:{e}")

            




utils = database_utils.DatabaseConnector()
engine = utils.init_db_engine("C:\\Users\\abshi\\OneDrive\\Documents\\IT\\Multination Retail Data Centralisation Project\\db_creds.yaml")
#get_db_tables = utils.list_db_tables this was a mistake as i called it using an instance which isn't nessecarry beacuse i used a static method, meaning i can jus call it directly. done below:
get_db_tables = DataExtractor.list_db_tables(engine)
table_name = 'legacy_users'
read_rds = DataExtractor.read_rds_table(engine, table_name)
print(read_rds)
link = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf'
retrieve_pdf = DataExtractor.retrieve_pdf_data(link)
#print(retrieve_pdf)
headers = {'x-api-key':'yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX'}
store_endpoint = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details/{store_number}'
return_stores_endpoint = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/number_stores'
