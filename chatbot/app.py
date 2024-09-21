from dotenv import load_dotenv 
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
import openai
import streamlit as st
import os

#Database configuration
user=os.getenv("DATABASE_USER")
password=os.getenv("DATABASE_PASSWORD")
host= os.getenv("DATABASE_HOST")
port= os.getenv("DATABASE_PORT")
database_name= os.getenv("DATABASE_NAME")

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
    db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
    return SQLDatabase.from_uri(db_uri)

# Validate SQL query
def is_valid_sql(query):
    # Basic check for SQL keywords
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'FROM', 'WHERE', 'JOIN', 'ORDER BY', 'GROUP BY', 'LIMIT']
    
    # Clean and check query, ensuring no Python objects or metadata are present
    query_clean = query.strip().upper()
    
    # Return True if valid SQL, False otherwise
    if any(keyword in query_clean for keyword in sql_keywords) and not re.search(r'[{}()=]|AIMessage', query):
        return True
    return False

# Azure OpenAI client initialization
def init_openai():
    openai.api_type = "azure"
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # URL de votre instance Azure OpenAI
    openai.api_version = "2023-05-15"  # Version de l'API à utiliser
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")  # Votre clé d'API Azure OpenAI

def get_sql_chain(db):
    template = """
    Du bist ein Datenanalyst in einem Unternehmen. Du interagierst mit einem Benutzer, der dir Fragen zur Unternehmensdatenbank stellt.
    Basierend auf dem unten angegebenen Tabellenschema, schreibe eine SQL-Abfrage, die die Frage des Benutzers beantwortet. 
    Antworte nur mit der SQL-Abfrage und füge keine zusätzlichen Zeichen, Metadaten oder Kommentare hinzu.

    <SCHEMA>{schema}</SCHEMA>

    Gesprächsverlauf: {chat_history}

    Frage: {question}
    SQL-Abfrage:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
  
    def openai_completion(prompt_value):
        if isinstance(prompt_value, ChatPromptTemplate):
            prompt_text = prompt_value.format()
        else:
            prompt_text = str(prompt_value)

        response = openai.Completion.create(
            engine="gpt-35-turbo",  # Nom du modèle déployé sur Azure
            prompt=prompt_text,
            max_tokens=500,
            temperature=0
        )
        return response.choices[0].text.strip()

    def get_schema(_):
        return db.get_table_info()

    return (
        RunnablePassthrough.assign(schema=get_schema)
        | prompt
        | openai_completion
        | StrOutputParser()
    )

def get_response(user_query: str, db: SQLDatabase, chat_history: list):
    sql_chain = get_sql_chain(db)
    
    response = sql_chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })
    
    # Check if the output is a valid SQL query
    if is_valid_sql(response):
        try:
            # If valid SQL, run it against the database
            return db.run(response)
        except Exception as e:
            return f"Fehler bei der SQL-Abfrage: {str(e)}"
    else:
        # Return an error message if the query is invalid
        return "Die generierte Ausgabe ist keine gültige SQL-Abfrage."

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hallo! Ich bin ein SQL-Assistent. Frag mich alles über deine Datenbank."),
    ]

load_dotenv()
init_openai()  # Initialise Azure OpenAI

st.set_page_config(page_title="Chat with MySQL", page_icon=":speech_balloon:")

st.title("Chat mit MySQL")

with st.sidebar:
    st.subheader("Einstellungen")
    st.write("Dies ist eine einfache Chat-Anwendung zur Interaktion mit einer MySQL-Datenbank. Verbinde dich mit der Datenbank und stelle Fragen.")
    
    st.text_input("Host", value="localhost", key="Host")
    st.text_input("Port", value="3306", key="Port")
    st.text_input("User", value="root", key="User")
    st.text_input("Password", type="password", value="admin", key="Password")
    st.text_input("Database", value="Chinook", key="Database")
    
    if st.button("Verbinden"):
        with st.spinner("Verbinde mit der Datenbank..."):
            db = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"]
            )
            st.session_state.db = db
            st.success("Erfolgreich mit der Datenbank verbunden!")
    
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Schreibe eine Nachricht...")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))