import os
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load the data from Excel
file_path = 'KI-HackathonxROSSMANN_Challenge_Ansprechpartner-Chatbot.xlsx'
df = pd.read_excel(file_path)

# Database connection parameters from .env file
config = {
    'user': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'host': os.getenv('DATABASE_HOST'),
    'database': os.getenv('DATABASE_NAME'),
    'port': int(os.getenv('DATABASE_PORT', '3306')),  # Provide a default value or ensure the .env has it
    'raise_on_warnings': True
}

# SQL statements to create tables
TABLES = {}
TABLES['departments'] = (
    "CREATE TABLE IF NOT EXISTS departments ("
    "  DepartmentID INT AUTO_INCREMENT PRIMARY KEY,"
    "  DepartmentName VARCHAR(255) NOT NULL"
    ")"
)

TABLES['positions'] = (
    "CREATE TABLE IF NOT EXISTS positions ("
    "  PositionID INT AUTO_INCREMENT PRIMARY KEY,"
    "  Title VARCHAR(255) NOT NULL,"
    "  Description TEXT"
    ")"
)

TABLES['employees'] = (
    "CREATE TABLE IF NOT EXISTS employees ("
    "  EmployeeID INT AUTO_INCREMENT PRIMARY KEY,"
    "  Name VARCHAR(255) NOT NULL,"
    "  Email VARCHAR(255),"
    "  Phone VARCHAR(50),"
    "  Location VARCHAR(255),"
    "  DepartmentID INT,"
    "  PositionID INT,"
    "  FOREIGN KEY (DepartmentID) REFERENCES departments(DepartmentID),"
    "  FOREIGN KEY (PositionID) REFERENCES positions(PositionID)"
    ")"
)

TABLES['responsibilities'] = (
    "CREATE TABLE IF NOT EXISTS responsibilities ("
    "  ResponsibilityID INT AUTO_INCREMENT PRIMARY KEY,"
    "  Description TEXT"
    ")"
)

TABLES['programs'] = (
    "CREATE TABLE IF NOT EXISTS programs ("
    "  ProgramID INT AUTO_INCREMENT PRIMARY KEY,"
    "  ProgramName VARCHAR(255) NOT NULL"
    ")"
)

TABLES['employee_responsibilities'] = (
    "CREATE TABLE IF NOT EXISTS employee_responsibilities ("
    "  EmployeeID INT,"
    "  ResponsibilityID INT,"
    "  FOREIGN KEY (EmployeeID) REFERENCES employees(EmployeeID),"
    "  FOREIGN KEY (ResponsibilityID) REFERENCES responsibilities(ResponsibilityID)"
    ")"
)

TABLES['employee_programs'] = (
    "CREATE TABLE IF NOT EXISTS employee_programs ("
    "  EmployeeID INT,"
    "  ProgramID INT,"
    "  FOREIGN KEY (EmployeeID) REFERENCES employees(EmployeeID),"
    "  FOREIGN KEY (ProgramID) REFERENCES programs(ProgramID)"
    ")"
)

def create_tables(cursor, tables):
    for table_name in tables:
        table_description = tables[table_name]
        try:
            print(f"Creating table {table_name}: ", end='')
            cursor.execute(table_description)
            print("OK")
        except Error as err:
            print(err.msg)

def main():
    conn = None  # Initialize conn to None
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            print('Connected to MySQL database')
            cursor = conn.cursor()

            # Create tables
            create_tables(cursor, TABLES)

            # Insert data into tables
            # Example: You will need to modify this to correctly map data from your Excel file to the appropriate tables
            # for i, row in df.iterrows():
            #     cursor.execute('INSERT INTO departments (DepartmentName) VALUES (%s)', (row['Abteilung'],))
            
            conn.commit()
            cursor.close()

    except Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print('Connection closed.')

if __name__ == '__main__':
    main()
