import pandas as pd
import numpy as np
import BCS_connector
import json
import re
import price_mapping_automation_v2 as pmauto
from datetime import datetime
import os
import pyodbc


def connector():
    server = "10.240.1.129"
    database = "asp_BUILDCONT"
    username = "buildcont_reports"
    password = "ASP4664bu"

    # connect with credentials
    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(connection_string)

    return connection


def p21_reader(supplier_id, connection):
    
    print("Connected to the BCS SSMS database!!")

    query = f"""
    with total_inv as (select
                p21_view_inv_mast.inv_mast_uid,
                SUM(COALESCE(p21_view_inv_loc.qty_on_hand, 0)) AS total_inv_QOH,
                MAX(p21_view_inv_loc.last_purchase_date) AS LPD
                FROM p21_view_inv_mast
                Left JOIN p21_view_inv_loc ON p21_view_inv_mast.inv_mast_uid = p21_view_inv_loc.inv_mast_uid
                GROUP BY
                p21_view_inv_mast.inv_mast_uid
                )
    select
    p21_item_view.item_id,
    p21_item_view.item_desc,
    p21_item_view.inv_mast_uid,
    p21_item_view.supplier_name,
    p21_item_view.supplier_part_no,
    p21_item_view.short_code,
    p21_item_view.delete_flag,
    MIN(p21_item_view.cost) AS Cost,
    MAX(p21_item_view.price1) AS P1,
    MAX(P21_item_view.list_price) AS LIST_PRICE,
    inv_mast_ud.on_vendor_price_book,
    total_inv.total_inv_QOH,
    total_inv.LPD,
    COUNT(l.location_id) AS stockable_locations_count
    FROM
    p21_item_view
    LEFT JOIN
        p21_view_inv_loc l ON p21_item_view.inv_mast_uid = l.inv_mast_uid AND l.stockable = 'Y'
    LEFT JOIN
        inv_mast_ud ON p21_item_view.inv_mast_uid = inv_mast_ud.inv_mast_uid
    LEFT JOIN
        total_inv ON p21_item_view.inv_mast_uid = total_inv.inv_mast_uid
	LEFT JOIN
		supplier_ud (nolock) on p21_item_view.supplier_id = supplier_ud.supplier_id
    WHERE
    p21_item_view.supplier_id IN ({str(supplier_id)})
    AND p21_item_view.delete_flag = 'N'
	AND supplier_ud.item_prefix = LEFT(p21_item_view.item_id, 3)
    
    GROUP BY
    p21_item_view.item_id,
    p21_item_view.item_desc,
    p21_item_view.inv_mast_uid,
    p21_item_view.supplier_name,
    p21_item_view.supplier_part_no,
    p21_item_view.short_code,
    p21_item_view.delete_flag,
    inv_mast_ud.on_vendor_price_book,
    total_inv.total_inv_QOH,
    total_inv.LPD
    ORDER BY
    inv_mast_ud.on_vendor_price_book, p21_item_view.item_id
    """

    # read data into DataFrame
    df = pd.read_sql_query(query, connection)

    return df



def main(folder_path):
    # get the suppliers file
    # iterate into each of the folder in the automation file and get the prefix
    # get the supplier id related to each of the prefix and get the data
    # store the data in an excel file in the folder with the already existing format

    with open("D:\\Price_mapping_automation\\suppliers.json", 'r+') as f:
        suppliers_data = json.load(f)

    mapperOB = pmauto.PBmapper()  
    folder_prefixes = mapperOB.get_prefixes(folder_path) # Will return the three letters of the input folders

    company_prefixes = []

    # check if the prefix is already a part of the company_json
    for folder in folder_prefixes:
        company_prefixes.append(folder)

    # get the folder paths of all the companies that need to be automated
    folder_paths = []

    for folder in os.listdir(folder_path):
        cur_prefix = folder[:3]
        if cur_prefix in company_prefixes:
            company = os.path.join(folder_path, folder)
            folder_paths.append(company)
            print(company)

    company_folders_paths = folder_paths


    connection = connector()

    # iterate over each of the company folder paths and read p21 data into excel files of the company
    for company in company_folders_paths:
        # get the base folder name and extract the first three letters as prefix
        prefix = os.path.basename(company)[:3]
        excel_sheet_name = f"{prefix}_P21_REVIEW"
        print(f"Opening Excel sheet: {excel_sheet_name}")

        for supplier in suppliers_data:
            if supplier['prefix'] == prefix:
                sup_id = supplier["supplier_id"]
                break

        df = p21_reader(sup_id, connection)
        print(df.head())

        current_time = datetime.now()
        day = current_time.day
        month = current_time.strftime("%b")
        year = current_time.year
        
        df.to_excel(f"{company}\\{excel_sheet_name}_{day}_{month}_{year}.xlsx", sheet_name="Worked", index=False)

    connection.close()



if __name__ == "__main__":
    
    folder_path = "D:\\Price mapping files - Onedrive setup"
 
    main(folder_path)
