import psycopg2
import logging
from datetime import datetime
import os
import csv
import pandas as pd
import time
import openpyxl


current_time = datetime.now()
fcurrent_time = current_time.strftime("%Y-%m-%d-%H-%M-%S")
log_file = os.path.join("D:\\Price_mapping_automation\\Logging_information", f"Pricing_automation_{fcurrent_time}.log")
logging.basicConfig(filename=log_file, level=logging.DEBUG)


# Connect to your PostgreSQL database
def connect_to_postgres(dbname, user, password, host, port):
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        logging.info("Connected to the PostgreSQL database successfully!")
        return conn
    
    except psycopg2.Error as e:
        logging.error("Unable to connect to the database")
        logging.error(e)
        return None


def read_data_into_table(connection, files):
    # replace the company_df with P21_folder
    
    # Ensure files is a list of file paths
    if isinstance(files, str):
        files = [files]
    
    print(files)

    cursor = connection.cursor()

    # read the folder and the files in it
    for i in files:
        company_df = pd.read_csv(i)

    
        now = datetime.now()
        

        # Extract the filename from the file path
        former_filename = os.path.basename(i)
        base_filename = former_filename.split('{')[0]  # Split on '{' and take the first part
        base_filename = base_filename.rstrip('_')  # Remove any trailing underscores


        # Extract date part and calculate week and weekday
        date_str = now.date()
        week_number = now.isocalendar()[1]  # Week number of the year
        weekday_number = now.weekday() + 1  # Convert to Monday=1, Sunday=7
        weekday_name = now.strftime('%A')   # Name of the weekday
        filename = base_filename  # get the i and then extract just the filename
        rowcount = len(company_df)  
        
        # add the other columns that are needed to be a part of the SQL database as well 

        #print(prefix)
        

        # SQL query to insert data into the table
        sql = """INSERT INTO report_stats (date_, week, weekday, filename, count_of_rows)
                VALUES (%s, %s, %s, %s, %s)"""
        
        
        # Execute the SQL query with the data from the current row
        cursor.execute(sql, (date_str, week_number, weekday_number, filename, rowcount))
    
    
    # Commit the transaction
    connection.commit()

    cursor.close()

