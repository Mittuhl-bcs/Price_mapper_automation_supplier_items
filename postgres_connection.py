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


def read_data_into_table(connection, P21_files, new_loop):
    # replace the company_df with P21_folder
    
    # to delete the existing data
    if new_loop == "yes":
        cursor = connection.cursor()
        
        sqld = "delete from p21_companyreview"
        cursor.execute(sqld)

        connection.commit()

        cursor.close()


    main_df = pd.DataFrame() 

    # read the folder and the files in it
    for i in P21_files:
        company_df = pd.read_excel(i)
        
        # filter only the discrepancy ones
        df = company_df[company_df["Discrepancy_type"] != "All right"]
        
        # save only the discrepancies in this df and concat the main df
        main_df = pd.concat([main_df, df], ignore_index=True)


    cursor = connection.cursor()

    for index, row in main_df.iterrows():
        """stspn = row["Stripped_supplier_PN"]
        prefix_db = row["Prefix_of_company"]
        matchedspn = row["Matched_pricingdoc_SPN"]
        prefixchk = company_df["Prefix_check"]
        onvpb = row["on_vendor_price_book"]
        onlpb = company_df["On_latest_vendorprice_book"]
        mismatch = company_df["Mismatch_check"]
        costpb= company_df["Cost_on_vendors_PB"]
        p1pb = company_df["P1_vendorsPB"] = ""
        lppb = company_df["Listprice_on_vendors_PB"] = ""
        costck = company_df["Cost_check"] = ""
        p1ck = company_df["P1_check"] = ""
        lpck = row["Listprice_check"] = ""
        dscrpnty = row["Discrepancy_type"]
        costp21 = row["Cost"]
        listp21 = row["LIST_PRICE"]
        p1p21 = row["P1"]
        """

        item_id = row["item_id"]
        prefix = row["Prefix_of_company"]
        supplier_part_number = row["supplier_part_no"]
        stripped_SPN = row["Stripped_supplier_PN"]
        matched_pricingdoc_SPN = row["Matched_pricingdoc_SPN"]
        prefix_check = row["Prefix_check"]
        on_vendor_price_book = row["on_vendor_price_book"]
        on_latest_price_book = row["On_latest_vendorprice_book"]
        pb_check = row["Mismatch_check"]
        cost = row["Cost"]
        p1 = row["P1"]
        list_price = row["LIST_PRICE"]
        cost_on_vendorPB = row["Cost_on_vendors_PB"]
        p1_on_vendorPB = row["P1_vendors_PB"]
        list_price_on_vendorPB = row["Listprice_on_vendors_PB"]
        cost_check = row["Cost_check"]
        p1_check = row["P1_check"]
        listprice_check = row["Listprice_check"]
        discrepancy_types = row["Discrepancy_type"]
        # add the other columns that are needed to be a part of the SQL database as well 

        #print(prefix)
        

        # SQL query to insert data into the table
        sql = """INSERT INTO p21_companyreview (item_id, prefix, supplier_part_number, stripped_spn, matched_pricingdoc_SPN, prefix_check,
                on_vendor_price_book, on_latest_price_book, pb_check, cost, p1, list_price, cost_on_vendorPB,
                p1_on_vendorPB, list_price_on_vendorPB, cost_check, p1_check, listprice_check, discrepancy_types)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        
        
        # Execute the SQL query with the data from the current row
        cursor.execute(sql, (item_id, prefix, supplier_part_number, stripped_SPN, matched_pricingdoc_SPN, prefix_check, on_vendor_price_book,
                        on_latest_price_book, pb_check, cost, p1, list_price, cost_on_vendorPB, p1_on_vendorPB,
                        list_price_on_vendorPB, cost_check, p1_check, listprice_check, discrepancy_types))
    
    
    # Commit the transaction
    connection.commit()

    cursor.close()

            
# export the csv from the database
def export_table_to_csv(connection, table_name, output_file, excel_output_file):
    try:
        cursor = connection.cursor()

        with open(output_file, 'w', encoding='utf-8', newline='') as file:
            csv_writer = csv.writer(file)

                        
            # Fetch data from the table and column headers
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            
            # Write column headers
            csv_writer.writerow(column_names)

            # Write rows
            for row in rows:
                csv_writer.writerow([
                    str(cell).encode('utf-8', errors='replace').decode('utf-8').replace('?', 'Error character')
                    for cell in row
                ])
        
        time.sleep(2)

        tempdf = pd.read_csv(output_file)
        sup_prefixes = tempdf["prefix"].unique().tolist()

        # Create an Excel writer object
        with pd.ExcelWriter(excel_output_file, engine='openpyxl') as writer:
        
        
            for prefix in sup_prefixes:
                tempdf_1 = tempdf[tempdf["prefix"] == prefix]

                # write the contents of the data into each of the sheet
                tempdf_1.to_excel(writer, sheet_name=prefix, index=False)

        
        print("Formatted Excel file saved !!")


    except psycopg2.Error as e:
        logging.error(f"Error exporting data from table '{table_name}' to CSV file")
        logging.error(e)

        raise ValueError(e)



