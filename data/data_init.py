import os
import pandas as pd
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load the data from Excel
file_path = 'data.xlsx'
df = pd.read_excel(file_path)

# Replace NaN values with an appropriate value for your schema, here using empty strings
df.fillna('', inplace=True)

# Database connection parameters from .env file
config = {
    'user': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
    'host': os.getenv('DATABASE_HOST'),
    'database': os.getenv('DATABASE_NAME'),
    'port': int(os.getenv('DATABASE_PORT', '3306')),
    'raise_on_warnings': True
}

# Sanitize column names to be compliant with MySQL naming (replace spaces and dashes)
df.columns = [c.replace(' ', '_').replace('-', '_') for c in df.columns]

# SQL statement to create a table with backticks around column names
column_definitions = ', '.join(f"`{col}` TEXT" for col in df.columns)  # Assuming all columns as TEXT for simplicity
CREATE_TABLE_QUERY = f"CREATE TABLE IF NOT EXISTS employee_data ({column_definitions})"

def create_table(cursor):
    try:
        cursor.execute(CREATE_TABLE_QUERY)
        print("Table created successfully")
    except Error as err:
        print("Failed to create table:", err)

def insert_data(cursor, df):
    # Prepare a SQL query to insert data into the table, with backticks
    placeholders = ', '.join(['%s'] * len(df.columns))
    columns = ', '.join(f"`{col}`" for col in df.columns)
    sql = f"INSERT INTO employee_data ({columns}) VALUES ({placeholders})"
    
    # Insert data row by row
    for i, row in df.iterrows():
        cursor.execute(sql, tuple(row.values))

def main():
    conn = None
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            print('Connected to MySQL database')
            cursor = conn.cursor()
            
            # Create table
            create_table(cursor)
            
            # Insert data into table
            insert_data(cursor, df)
            
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
