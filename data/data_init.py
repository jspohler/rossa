import pandas as pd
import sqlite3

# Load the data from Excel
file_path = 'KI-HackathonxROSSMANN_Challenge_Ansprechpartner-Chatbot.xlsx'
data = pd.read_excel(file_path, sheet_name='Tabelle1')

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('rossmann_database.db')
cursor = conn.cursor()

# Create a table in the database
cursor.execute('''
    CREATE TABLE IF NOT EXISTS rossmann_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        department TEXT,
        position TEXT,
        responsibility_areas TEXT,
        email TEXT,
        phone TEXT,
        location TEXT,
        position_description TEXT,
        supported_programs TEXT
    )
''')

# Insert data into the table
for _, row in data.iterrows():
    cursor.execute('''
        INSERT INTO rossmann_contacts (name, department, position, responsibility_areas, email, phone, location, position_description, supported_programs)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (row['Name'], row['Abteilung'], row['Position'], row['Zuständigkeitsbereiche'], row['E-Mail-Adresse'], row['Telefonnummer'], row['Standort'], row['Beschreibung der Position und Zuständigkeiten bei Problemen'], row['Betreute Programme']))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Data has been inserted into the database.")
