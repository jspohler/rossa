import pandas as pd
import sqlite3
import os

# Load the Excel file
file_path = 'data\KI-HackathonxROSSMANN_Challenge_Ansprechpartner-Chatbot.xlsx'
data = pd.read_excel(file_path, sheet_name='Tabelle1')



# Define the path where the SQLite database will be saved
db_file = os.path.join(os.getcwd(), 'rossmann_chatbot_data.db') 

# Create a connection to the database
conn = sqlite3.connect(db_file)

# Convert the DataFrame to a SQL table
data.to_sql('contacts', conn, if_exists='replace', index=False)

# Verify by listing the tables in the database
tables_in_db = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)

# Close the connection to the database
conn.close()

