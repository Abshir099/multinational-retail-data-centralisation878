import yaml
from sqlalchemy import create_engine
from sqlalchemy.sql import text

class DatabaseConnector:
    def read_db_creds(self,db_creds):
        with open(db_creds, 'r') as file:
            db_creds = yaml.safe_load(file)
            return db_creds
    def read_sales_db_creds(self,sales_creds_file):
        with open(sales_creds_file, 'r') as db_file:
            sales_data_db = yaml.safe_load(db_file)
            return sales_data_db
            

    def init_db_engine(self, db_creds_file):
        creds = self.read_db_creds(db_creds_file)
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        USERNAME = creds.get('USERNAME') or creds.get('RDS_USER')
        PASSWORD = creds.get('PASSWORD') or creds.get('RDS_PASSWORD')
        HOST = creds.get('Host') or creds.get('RDS_HOST')
        PORT = creds.get('PORT') or creds.get('RDS_PORT')
        DATABASE = creds.get('DATABASE') or creds.get('RDS_DATABASE')
        engine_url = f"{DATABASE_TYPE}+{DBAPI}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        engine = create_engine(engine_url)
        return engine
    @staticmethod
    def list_db_tables(engine):
         with engine.connect() as connection:
            result = connection.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = \'public\';"))
            for table in result.fetchall():
                #print(f"Loaded tables: {table}")
                #print(table)
                return table
            
    def upload_to_db(self, df, table_name, sales_creds_file):
        creds = self.read_sales_db_creds(sales_creds_file)
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        USERNAME = creds.get('USERNAME') or creds.get('RDS_USER')
        PASSWORD = creds.get('PASSWORD') or creds.get('RDS_PASSWORD')
        HOST = creds.get('Host') or creds.get('RDS_HOST')
        PORT = creds.get('PORT') or creds.get('RDS_PORT')
        DATABASE = creds.get('DATABASE') or creds.get('RDS_DATABASE')
        upload_string = f"{DATABASE_TYPE}+{DBAPI}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        upload_engine = create_engine(upload_string)
        df.to_sql(table_name,upload_engine,if_exists='replace',index=False)

db_connector = DatabaseConnector()
engine = db_connector.init_db_engine("C:\\Users\\abshi\\OneDrive\\Documents\\IT\\Multination Retail Data Centralisation Project\\db_creds.yaml")

if __name__ == "__main__":
    from DataExtractor import DataExtractor
    extractor = DataExtractor()
    link = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf'
    import data_cleaning
    user_data_to_clean = extractor.read_rds_table(engine,'legacy_users')
    card_data_to_clean = extractor.retrieve_pdf_data(link)
    cleaned_user_data = data_cleaning.DataCleaning.clean_card_data(user_data_to_clean)
    cleaned_card_data = data_cleaning.DataCleaning.clean_card_data(card_data_to_clean)
    db_connector.clean_and_upload(engine, 'legacy_users', 'link', "C:\\Users\\abshi\\OneDrive\\Documents\\IT\\Multination Retail Data Centralisation Project\\sales_data_db.yaml")
    db_connector.list_db_tables(engine)
