'''
Basic database connection code to create a db_url for SQLAlchemy command execution.

NOTES: 
  - Called in query.py to establish a database connection
  - For additional database connection information, see: https://docs.sqlalchemy.org/en/20/dialects/index.html

TO DO: 
  - Add functionality to incorporate Oracle as a database option: "oracle+oracledb://scott:tiger@127.0.0.1:1521/?service_name=freepdb1"
'''
import json
import getpass
import subprocess

def get_db_url(config_file_path):
  '''
  Defines a databse connection URL.  

  Parameters: 
    config_file_path: path to json configuration file. 

  Returns:
    The config as a json object and the appropriate db_url.
  '''
  with open(config_file_path) as f:
    config = json.load(f)

  #connection URL for Postgres 
  if config["src_name"].lower() == "postgres":
      if "DO_NOT_EDIT_IF_YOU_WISH_TO_ENTER_IT_ON_DOCKER_RUN" in config["src_args"].values():
        config["src_args"]["password"] = getpass.getpass(f"Enter Password for {config['src_args']['user']}: ")
      password = config["src_args"]["password"].replace("@", "%40").replace("/", "%2F")
      db_url = f'postgresql+psycopg2://{config["src_args"]["user"]}:{password}@{config["src_args"]["host"]}/{config["src_args"]["dbname"]}?options={config["src_args"]["options"]}'

  elif config["src_name"].lower() == "odbc":
    #connection URL for Snowflake
    if config["src_args"]["Driver"] == "SnowflakeDSIIDriver":  
        if "DO_NOT_EDIT_IF_YOU_WISH_TO_ENTER_IT_ON_DOCKER_RUN" in config["src_args"].values():
            config["src_args"]["PWD"] = getpass.getpass(f"Enter Password for {config['src_args']['UID']}: ")
        password = config["src_args"]["PWD"].replace("@", "%40").replace("/", "%2F")
        db_url = f'snowflake://{config["src_args"]["UID"]}:{password}@{config["src_args"]["Server"]}/{config["src_args"]["Database"]}/{config["src_args"]["SCHEMA"]}?warehouse={config["src_args"]["WAREHOUSE"]}&role={config["src_args"]["Role"]}'

    #connection URL for MS SQL: Active Directory autheticated user
    if (config["src_args"]["Driver"].startswith("ODBC Driver") and config["src_args"]["Trusted_Connection"] == "yes"):
        config["src_args"]["UID"] = None
        config["src_args"]["PWD"] = None
        print("Trusted_Connection=yes; Using Kerberos Authentication...")
        principal = input("Provide database username including domain in uppercase (e.g. username@CHOP.EDU): ")
        subprocess.run(["kinit", principal])
        db_url = f'mssql+pyodbc://@{config["src_args"]["Server"]}:{config["src_args"]["Port"]}/{config["src_args"]["Database"]}?trusted_connection=yes&&TrustServerCertificate=yes&driver={config["src_args"]["Driver"]}&schema={config["src_site"]["db_schema"]}'

    #connection URL for MS SQL: database user authetication
    elif (config["src_args"]["Driver"].startswith("ODBC Driver") and config["src_args"]["Trusted_Connection"] == "N/A"):  
        config["src_args"]["Trusted_Connection"] = None
        if "DO_NOT_EDIT_IF_YOU_WISH_TO_ENTER_IT_ON_DOCKER_RUN" in config["src_args"].values():
            config["src_args"]["PWD"] = getpass.getpass(f"Enter Password for {config['src_args']['UID']}: ")
        password = config["src_args"]["PWD"].replace("@", "%40").replace("/", "%2F")
        db_url = f'mssql+pyodbc://{config["src_args"]["UID"]}:{password}@{config["src_args"]["Server"]}:{config["src_args"]["Port"]}/{config["src_args"]["Database"]}?TrustServerCertificate=yes&driver={config["src_args"]["Driver"]}&schema={config["src_site"]["db_schema"]}'
    
  return config, db_url