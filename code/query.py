'''
Query-specific code for the request

Here are some suggestions on getting started writing a query in Python using a Docker container

NOTES:
    - Calls get_db_url from db_connection.py to establish database connection using AQLAlchemy
    - Executes SQLAlchemy command against the database provided.
''' 
import sqlalchemy as sqlalc
import csv
from db_connection import get_db_url
import datetime
import time
import logging
import pandas as pd
import argparse
import os
# Additional packages may be needed for your query and may need to be added to the requirements.txt file to be installed within the container.

#silence SQLAlchemy warning message & disable printing sql commands for snowflake
sqlalc.util.deprecations.SILENCE_UBER_WARNING = True
snowflake_logger = logging.getLogger('snowflake.connector')
snowflake_logger.setLevel(logging.WARNING)

config_file_path = "/app/config_file"
config, db_url = get_db_url(config_file_path) #get config and db_url from get_db_url

# create log file
logging.basicConfig(filename = f'/results/{config["src_site"]["SiteName"]}.log', level=logging.INFO, format='%(message)s', datefmt='%Y-%m-%d %H:%M:%S', filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)


def load_codeset(conn, rdbms, current_temp_tables, name, tbl_name=None, col_types='iccc', overwrite=False):
    '''
        Create a temporary db table with a codeset as per the query
            - Reads the named codeset from a CSV file, and creates a like-named temporary table in the database with the contents.
            - Expects the csv file to be in the specs directory, to have a header, and to contain four columns:
            * concept_id - integer
            * concept_name - string
            * concept_code - string
            * vocabulary_id - string
  
        Parameters:
            conn: a connection to the database into which to load the codeset
            rdbms: relational database management system software associated with the current connection
            current_temp_tables: a list of temporary tables associated with the current connection
            name: the name of the codeset. Typically just the file name without `.csv` suffix, but if for some reason you've expanded the  directory tree under `specs`, you may prefix it with subdirectories
            tbl_name: an optional name for the table, if you want it to differ from `name`
            col_types: an optional string of i's & c's representing column types for a codeset, defaults to 'iccc' where i corresponds to INTEGER and c corresponds to VARCHAR(256)
            overwrite: whether to overwrite an existing table of the same name. Temporary tables will only overwrite when the tbl_name is present in the current_temp_tables attribute. Defaults to False. 

        Returns:
            tbl_name: name of temporary table containing the codeset
                NOTE: table name not specified in double quotes ("") & therefore not case sensitive
        '''
    # Get column types
    type_mapping = {
        'i': ('INTEGER', 'Int64'),
        'c': ('VARCHAR(256)', 'str')
    }

    # Generate column types for database and pandas df
    db_col_type_list = [type_mapping[letter][0] for letter in col_types]
    df_col_type_list = [type_mapping[letter][1] for letter in col_types]

    with open(f'specs/{name}.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        df_column_names = next(reader)

    df_col_dict = dict(zip(df_column_names, df_col_type_list))     

    # Read csv file 
    df = pd.read_csv(f'specs/{name}.csv', dtype=df_col_dict)
    df.columns = df.columns.str.lower() # convert all column names to lowercase for consistency 
    col_name_list = [column_name for column_name in df.columns] #extract column names from df 

    col_dict = dict(zip(col_name_list, db_col_type_list)) 
    # Create DDL string using column and column type information
    column_ddl_string = ', '.join(f"{col} {dtype}" for col, dtype in col_dict.items())

    # Set tbl_name if not already declared
    if tbl_name is None:
        tbl_name = name.split('/')[-1]

    try:
        if rdbms == 'mssql': 
            tbl_name = f'#{tbl_name}'
            if overwrite:
                if tbl_name in current_temp_tables:
                    drop_tbl=f'DROP TABLE IF EXISTS {tbl_name};'
                    conn.execute(drop_tbl)
            create_table_sql = f"CREATE TABLE {tbl_name} ({column_ddl_string});"
        elif rdbms == 'postgres' or rdbms == 'snowflake':
            if overwrite:
                if tbl_name in current_temp_tables:
                    drop_tbl=f'DROP TABLE IF EXISTS {tbl_name};'
                    conn.execute(drop_tbl)
            create_table_sql = f"CREATE TEMP TABLE {tbl_name} ({column_ddl_string});"

        # Create temporary table  
        conn.execute(create_table_sql)
        logging.info("Created a temporary table named %s", tbl_name)
        current_temp_tables.append(tbl_name)

        # Insert data into the temporary table
        df.to_sql(tbl_name, conn, if_exists='append', index=False)

        return tbl_name
        
    except Exception as e:
        logging.info("Unable to load codeset into temporary table %s", e)

    
def create_temp_table(conn, rdbms, tbl_name, current_temp_tables, query, overwrite=False):
    '''
        Outputs a schemaless temporary table to the database. 
        Temporary tables will only overwrite when the tbl_name is present in the current_temp_tables attribute.
        
        Parameters:   
            conn: a connection to the database into which to create the temporary table        
            rdbms: relational database management system software associated with the current connection
            tbl_name: the name of the temporary table to create
            current_temp_tables: a list of temporary tables associated with the current connection
            query: a query string to execute for table creation
            overwrite: whether to overwrite an existing table of the same name. If a table of the same name is not present in the current_temp_tables attribute, overwrite will be set to False. Defaults to False

        Returns:
            tbl_name: name of the temporary table created
                NOTE: table name is specified in double quotes ("") & therefore is case sensitive
        '''
    try:
        if rdbms == 'mssql':
            tbl_name = '#'+tbl_name
            if overwrite:
                if tbl_name in current_temp_tables:
                    drop_tbl=f'DROP TABLE IF EXISTS "{tbl_name}";'
                    conn.execute(drop_tbl)
            split_query = query.split('FROM',1)
            select_statement = split_query[0]
            from_statement = 'FROM' + split_query[1]
            statement = f'''{select_statement}INTO "{tbl_name}" {from_statement}'''

        elif rdbms == 'postgres' or rdbms == 'snowflake':
            if overwrite:
                if tbl_name in current_temp_tables:
                    drop_tbl=f'DROP TABLE IF EXISTS "{tbl_name}";'
                    conn.execute(drop_tbl)
            statement = f'''CREATE TEMP TABLE "{tbl_name}" AS {query}'''
        
        # Create temporary table  
        conn.execute(statement)
        logging.info("Created a temporary table named %s", tbl_name)
        current_temp_tables.append(tbl_name)
        
        return tbl_name
    
    except Exception as e:
        logging.info("Unable to create temporary table %s", e)


def calc_days_between_dates(rdbms, date_col1, date_col2):
    '''
    SQL command to calculate days between dates according to the rdbms associated with the current connection
    
    Parameters:        
        rdbms: relational database management system software associated with the current connection
        date_col1: first column for date difference calculation
        date_col2: second column for date difference calculation

    Returns:
        calc: database-specific date difference query 
    '''
    if rdbms == 'mssql' or rdbms == 'snowflake':
        calc = f"""DATEDIFF(day, "{date_col1}", "{date_col2}")"""

    elif rdbms == 'postgres':
        calc = f"{date_col2} - {date_col1}"

    return calc


def get_table_one(cohort, cohort_name, cat_vars, cont_vars):
    '''
    Generate Table 1

    Parameters: 
        cohort: final dataframe of merged and modified cohort data
        cohort_name: cohort name as a string for naming the output table
        cat_vars: list of categorical variables
        cont_vars: list of continuous variables

    Returns:
        aql_query2_{cohort_name}_table1.csv
    '''
    column_mapping = {col: col.lower() for col in cohort.columns if 'age_at_HEI' not in col} # do not change case of columns like 'age_at_HEI...'
    cohort.rename(columns=column_mapping, inplace=True)

    tbl_1_results = []

    tbl_1_results.append({
                'block': "Total",
                'variable': "Total",
                'Characteristics': "Total",
                'var_type': 'Total',
                'value': cohort.shape[0]
            })

    # Loop through each cont variable
    stats = {"mean":"mean", "std":"sd", "25%":"quantile_25", "75%":"quantile_75"}
    for var in cont_vars:
        description = cohort[var].describe()
        for stat, value in description.items():
            if stat in stats.keys():
                char = stats[stat]
                row = {
                    'block': var,
                    'variable': var + '_' + char,
                    'Characteristics': char,
                    'var_type': 'cont',
                    'value': value
                }
                tbl_1_results.append(row)
        median = cohort[var].median() # calculate the median
        tbl_1_results.append({
                'block': var,
                'variable': var + '_median',
                'Characteristics': 'median',
                'var_type': 'cont',
                'value': median
            })
        
    # Loop through each cat variable
    for var in cat_vars:
        counts = cohort[var].value_counts(dropna = False)
        for char, value in counts.items():
            row = {
                'block': var,
                'variable': var if char is None else var + '_' + str(char),
                'Characteristics': char,
                'var_type': 'cat',
                'value': value
            }
            tbl_1_results.append(row)

    # Generate the resulting dataframe and save to csv file
    tbl_1_results_df = pd.DataFrame(tbl_1_results)
    tbl_1_results_df.to_csv(f"/results/aql_query2_{cohort_name}_table1.csv", index=False)


# Add query-specific functions
# Here is an example:
def get_pat_count(attr_list, conn, schema, tables, table_cols):
    '''
    Baidc function to get patient count from the demographic table

    Parameters: 
        attr_list: current list of attrition steps to append to
        conn: a connection to the database
        schema: schema to search against
        tables: dictionary of table mappings to handle case-sensitivity
        table_cols: dictionary of table name mapping to column names to handle case-sensitivity
    '''
    total_patients = conn.execute(f'''SELECT COUNT(*) FROM (SELECT DISTINCT "{table_cols['demographic']['patid']}" FROM {schema}."{tables['demographic']}") AS q01''')
    attr_list.append(["Total patients", "pat_count", total_patients.scalar(), config["src_site"]["SiteName"], datetime.datetime.now(), time.process_time()])


def main():
    try:
        current_temp_tables = []
        results = {}
        results["Query Start Time"] = datetime.datetime.now()

        logging.info("PCORnet Advanced Querying System (PAQS)")
        logging.info("PAQS Version: 1.0")
        logging.info("Query Title - to be printed at top of log ")
        
        logging.info("Execution Details:")
        logging.info("\tRun Date: %s", datetime.datetime.today().date())
        logging.info("\tConfig Info:")
        logging.info("\t\tSite: %s", config["src_site"]["SiteName"])
        logging.info("\t\tsrc_name: %s", config["src_name"])

        if config["src_name"] == "odbc":
            logging.info("\t\tDriver: %s", config["src_args"]["Driver"])
        
        # Define query-specific variables, for example:
        min_date_cutoff = ""
        max_date_cutoff = ""
        cat_vars = []
        cont_vars = []
        attr_list = []

        # create dictionaries to map table names and certain column names for handling case sensitivity 
        tables = {}
        table_cols = {}
    
        if config["src_name"] == "odbc" and config["src_args"]["Driver"] == 'ODBC Driver 18 for SQL Server':
            engine = sqlalc.create_engine(db_url, fast_executemany=True)
        else: 
            engine = sqlalc.create_engine(db_url)       

        with engine.connect() as conn, conn.begin():
            inspector = sqlalc.inspect(engine)
            logging.info("Getting table and column information")
            #get schema, table names, and column names 
            if config["src_name"] == "odbc" and config["src_args"]["Driver"] == "SnowflakeDSIIDriver":  
                rdbms = 'snowflake'
                schema = config["src_args"]["SCHEMA"]
                result = conn.execute(f"SHOW TABLES IN SCHEMA {schema}") # snowflake uses different logic for getting table & column names in the proper case 
                for table_name in [row[1] for row in result]:
                    tables[table_name.lower()] = table_name
                # if CDM tables are stored as views instead of tables, get view names
                if 'demographic' not in tables.keys() or 'diagnosis' not in tables.keys():
                    logging.info("Getting view names")
                    tables = {}
                    result = conn.execute(f"SHOW VIEWS IN SCHEMA {schema}")  
                    for view_name in [row[1] for row in result]:
                        tables[view_name.lower()] = view_name
                #get column names
                for table in tables.keys():
                    col_dict = {}
                    cols = conn.execute(f"SELECT COLUMN_NAME FROM information_schema.columns WHERE TABLE_NAME = '{tables[table]}' AND TABLE_SCHEMA = '{schema}'")
                    for column in [row[0] for row in cols]:
                        col_dict[column.lower()] = column
                    table_cols[table] = col_dict

            else:
                if config["src_name"] == "Postgres":
                    rdbms = 'postgres'
                else:
                    rdbms = 'mssql'
                schema = config["src_site"]["db_schema"]
                # try getting table names
                for table_name in inspector.get_table_names(schema=schema):
                    tables[table_name.lower()] = table_name
                # if CDM tables are stored as views instead of tables, get view names
                if 'demographic' not in tables.keys() or 'diagnosis' not in tables.keys():
                    logging.info("Getting view names")
                    tables = {}
                    for view_name in inspector.get_view_names(schema=schema):
                        tables[view_name.lower()] = view_name 
                #get column names
                for table in tables.keys():
                    col_dict = {}
                    for column in inspector.get_columns(tables[table], schema=schema):
                        col_dict[column['name'].lower()] = column['name']
                    table_cols[table] = col_dict
                        
            # Call query-specific functions 
            logging.info("Add log statements for query-specific functions")
            # Here is an example!
            logging.info("Get total patient count")
            get_pat_count(attr_list, conn, schema, tables, table_cols)


            # Create attrition.csv file, modify as needed. 
            logging.info("Saving attrition...")
            attr_results = [{"cohort": attr[0], "group": attr[1], "persons": attr[2], "qry_site": attr[3],"stamp": attr[4],"used": attr[5]} for attr in attr_list]
            headers = ["cohort","group","persons","qry_site","stamp","used"]
            with open("/results/attrition.csv", mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                for row in attr_results:
                    writer.writerow(row)

            
            # Continue to call additional query-specific functions (as needed)
            logging.info("Add more log statements")


            results["Query End Time"] = datetime.datetime.now()
            results["Total Run time"] = results["Query End Time"]-results["Query Start Time"]
            
            # Create signature.csv file
            logging.info("Generating signature file")
            signature_results = [{"Query Start Time": results["Query Start Time"], "Query End Time": results["Query End Time"], "Total Run Time": results["Total Run time"]}]
            headers = ["Query Start Time", "Query End Time", "Total Run Time"]
            with open("/results/your_query_signature.csv", mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=headers)
                writer.writeheader()
                for row in signature_results:
                    writer.writerow(row)

            logging.info("Closing connection...")   
        logging.info("Done.")

    except Exception as e:
        logging.info("Error in query execution: %s", e)
        logging.info("Please contact qf@pcornet.org for error handling assistance.")
        raise(e)
        
if __name__ == "__main__":
    main()
