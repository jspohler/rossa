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
    'port': os.getenv('DATABASE_PORT'),
    'raise_on_warnings': True
}

# SQL statements to create tables
TABLES = {}
TABLES['departments'] = (
    "CREATE TABLE IF NOT EXISTS departments ("
    "  DepartmentID INT AUTO_INCREMENT PRIMARY KEY,"
    "  DepartmentName VARCHAR(255) NOT NULL"
    ")")

TABLES['positions'] = (
    "CREATE TABLE IF NOT EXISTS positions ("
    "  PositionID INT AUTO_INCREMENT PRIMARY KEY,"
    "  Title VARCHAR(255) NOT NULL,"
    "  Description TEXT"
    ")")

# Add more CREATE TABLE statements for other tables

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
    # Establishing a connection to the database
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            print('Connected to MySQL database')
            cursor = conn.cursor()
            
            # Create tables
            create_tables(cursor, TABLES)
            
            # Insert data into tables (example for departments)
            for i, row in df.iterrows():
                cursor.execute('INSERT INTO departments (DepartmentName) VALUES (%s)', (row['Abteilung'],))
            
            conn.commit()
            cursor.close()
            
    except Error as e:
        print(e)
    finally:
        if conn.is_connected():
            conn.close()
            print('Connection closed.')

if __name__ == '__main__':
    main()
