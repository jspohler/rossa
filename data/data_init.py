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

            # Assume departments and positions are unique and need to be entered once
            # Temporary storage to avoid inserting duplicates
            inserted_departments = {}
            inserted_positions = {}

            # Iterate over the DataFrame to insert data
            for i, row in df.iterrows():
                # Insert department if not already done
                if row['Abteilung'] not in inserted_departments:
                    cursor.execute('INSERT INTO departments (DepartmentName) VALUES (%s)', (row['Abteilung'],))
                    conn.commit()  # Commit after each insert to obtain ID
                    inserted_departments[row['Abteilung']] = cursor.lastrowid
                
                # Insert position if not already done
                if row['Position'] not in inserted_positions:
                    cursor.execute('INSERT INTO positions (Title, Description) VALUES (%s, %s)', (row['Position'], row['Beschreibung der Position und Zuständigkeiten bei Problemen']))
                    conn.commit()  # Commit to get ID
                    inserted_positions[row['Position']] = cursor.lastrowid
                
                # Insert employee data
                cursor.execute('''
                    INSERT INTO employees (Name, Email, Phone, Location, DepartmentID, PositionID)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (
                        row['Name'],
                        row['E-Mail-Adresse'],
                        row['Telefonnummer'],
                        row['Standort'],
                        inserted_departments[row['Abteilung']],
                        inserted_positions[row['Position']]
                    )
                )
                employee_id = cursor.lastrowid

                # Handle responsibilities (simplifying as a single text field split by commas)
                responsibilities = row['Zuständigkeitsbereiche'].split(',')
                for resp in responsibilities:
                    resp = resp.strip()
                    # Insert responsibility if new
                    cursor.execute('SELECT ResponsibilityID FROM responsibilities WHERE Description = %s', (resp,))
                    res = cursor.fetchone()
                    if res:
                        responsibility_id = res[0]
                    else:
                        cursor.execute('INSERT INTO responsibilities (Description) VALUES (%s)', (resp,))
                        conn.commit()
                        responsibility_id = cursor.lastrowid
                    
                    # Link employee to responsibility
                    cursor.execute('INSERT INTO employee_responsibilities (EmployeeID, ResponsibilityID) VALUES (%s, %s)', (employee_id, responsibility_id))
                
                # Handle programs (assuming comma-separated as well)
                programs = row['Betreute Programme'].split(',')
                for prog in programs:
                    prog = prog.strip()
                    # Insert program if new
                    cursor.execute('SELECT ProgramID FROM programs WHERE ProgramName = %s', (prog,))
                    result = cursor.fetchone()
                    if result:
                        program_id = result[0]
                    else:
                        cursor.execute('INSERT INTO programs (ProgramName) VALUES (%s)', (prog,))
                        conn.commit()
                        program_id = cursor.lastrowid
                    
                    # Link employee to program
                    cursor.execute('INSERT INTO employee_programs (EmployeeID, ProgramID) VALUES (%s, %s)', (employee_id, program_id))
                
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
