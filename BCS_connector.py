import pyodbc
import pandas as pd
import warnings
import dask.dataframe as dd
import csv


# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)



def connect_db(query):

    server = "10.240.1.129"
    database = "asp_BUILDCONT"
    username = "buildcont_reports"
    password = "ASP4664bu"


    # connect with credentials
    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(connection_string)

    print("Connected to the BCS SSMS database!!")

    # read data into DataFrame
    df = pd.read_sql_query(query, connection)

        
    # return df
    return df, connection



def reader_df(supplier_id):
      
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
	WHERE
	p21_item_view.supplier_id IN ({str(supplier_id)})
	AND p21_item_view.delete_flag = 'N'

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
      
	df, connection = connect_db(query)

	connection.close()

	return df  
	