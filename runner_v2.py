# this is main file that will be used for running other files for DB connection, data processing
import postgres_connection as pgs
import price_mapping_automation_v2 as pmauto
import postgres_stats_update as pgsstats
from datetime import datetime 
import argparse, sys
import logging
import os
import json
import mailer
import time
import subprocess

dbname = 'BCS_items'
user = 'postgres'
password = 'post@BCS'
host = 'localhost' 
port = '5432'  # Default PostgreSQL port is 5432


current_time = datetime.now()
day = current_time.day
month =  current_time.strftime("%b")
year = current_time.year


table_name = "p21_companyreview"  # Replace with the actual table name
output_file = f"D:\\Discrepancy files\\Price_matching_report_{day}_{month}_{year}.csv"  # Replace with the dedicated file path 


def run_script(script_name):
    try:
        # Run the script using subprocess.run() to capture output and errors
        result = subprocess.run(['python', script_name], capture_output=True, text=True)
        
        # Print the output and errors, if any
        print(f"Output of {script_name}:\n{result.stdout}")
        if result.stderr:
            print(f"Error in {script_name}:\n{result.stderr}")
    except Exception as e:
        print(f"Failed to run {script_name}: {e}")


def runner_main(folder_path, company_json_path, new_loop_check):

    # Running the two scripts
    run_script('deletion_code.py')
    time.sleep(2)
    run_script('P21_review_file.py')
        
    mapper = pmauto.PBmapper()
    P21_files = mapper.main(folder_path, company_json_path)

    config_file = "D:\\Price_mapping_Automation\\config_file.json"


    # writting the file paths of P21 processed files in config file json
    with open(config_file, "r+") as cnf:
        cnfdata = json.load(cnf)

    for file in P21_files:
        cnfdata["P21_files"].append(file)

    with open(config_file, "w") as cnf:
        json.dump(cnfdata, cnf, indent=4)


    logging.info("Files are saved in the located folder.")
    logging.info(f"Matching process finished")

    ### till here

    current_time = datetime.now()
    day = current_time.day
    month = current_time.strftime("%b")
    year = current_time.year

    # database table name and output file name
    table_name = "p21_companyreview"
    output_file = f"D:\\Price_mapping_discrepancies\\Discrepancies - Orange - Price_matching_report_{day}_{month}_{year}.csv"
    excel_output_file = f"D:\\Price_mapping_discrepancies\\Formatted Discrepancies - Orange - Price_matching_report_{day}_{month}_{year}.xlsx"


    conn = pgs.connect_to_postgres(dbname, user, password, host, port)
    pgs.read_data_into_table(conn, P21_files, new_loop_check)
    pgs.export_table_to_csv(conn, table_name, output_file, excel_output_file)

    conn.close()
    
    conn_stat = pgsstats.connect_to_postgres(dbname, user, password, host, port)

    # read the stats into the stats table
    pgsstats.read_data_into_table(conn_stat, output_file)
    conn_stat.close()
    

    attachment_display_name = f"Price_matching_discrepancies_report_{day}_{month}_{year}.csv"
    # Send mails to the recipients with the attachments
    # mailresult = mailer.send_email(output_file, attachment_display_name)
    
    mailresult = True

    # give a final output
    if mailresult == True:
        print("Process fininshed. Mails have been sent with attachement!")
        #logging.info("Process fininshed. Mails have been sent with attachement!")

# get the inputs of the file paths and store it in the json file

if __name__ == "__main__":

    start_time = time.time()

    parser = argparse.ArgumentParser(description= "Mapping company and pricing files")
    parser.add_argument("--folder_path", help="Give the master folder path", required=True)
    parser.add_argument("--company_json_path", help= "Give the finished list of companies json file path", required=True)
    parser.add_argument("--new_loop", help= "Say if it is a new loop or a loop from middle", required= True)
    parser.add_argument("--mail", help= "Say if it is a new loop or a loop from middle", required= True)
    args = parser.parse_args()

    folder_path = args.folder_path
    company_json_path = args.company_json_path
    new_loop_check = args.new_loop


    if new_loop_check == "yes":
        with open(company_json_path, "w") as cjs:
            data = {"Prefixes" : []}
            json.dump(data, cjs, indent=4)

        config_file = "D:\\Price_mapping_Automation\\config_file.json"

        # writting the empty file in config file json
        with open(config_file, "w") as cnf:
            cnfdata = {"P21_files":[]}
            json.dump(cnfdata, cnf, indent=4)


    elif new_loop_check == "no":
        pass
    
    else:
        raise ValueError("Automation information (new loop) not given!!")
    
    # run the main function
    runner_main(folder_path, company_json_path, new_loop_check)

    end_time = (time.time() - start_time) /60
    print("____________________________________________________________________")
    print(" ")
    print(f"Time taken : {end_time:2f} mins")
    print("____________________________________________________________________")

    
# use subprocess for running the scripts

# after the run, save an empty json file. 