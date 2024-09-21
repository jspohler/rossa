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

# Azure OpenAI client initialization
def init_openai():
    openai.api_type = "azure"
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # URL de votre instance Azure OpenAI
    openai.api_version = "2023-05-15"  # Version de l'API à utiliser
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")  # Votre clé d'API Azure OpenAI

def get_sql_chain(db):
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
    
    For example:
    Question: which 3 artists have the most tracks?
    SQL Query: SELECT ArtistId, COUNT(*) as track_count FROM Track GROUP BY ArtistId ORDER BY track_count DESC LIMIT 3;
    Question: Name 10 artists
    SQL Query: SELECT Name FROM Artist LIMIT 10;
    
    Your turn:
    
    Question: {question}
    SQL Query:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
  
    def openai_completion(prompt_text):
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
    
    template = """
    You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, question, sql query, and sql response, write a natural language response.
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}"""
    
    prompt = ChatPromptTemplate.from_template(template)
  
    def openai_completion(prompt_text):
        response = openai.Completion.create(
            engine="gpt-35-turbo",  # Nom du modèle déployé sur Azure
            prompt=prompt_text,
            max_tokens=500,
            temperature=0
        )
        return response.choices[0].text.strip()

    chain = (
        RunnablePassthrough.assign(query=sql_chain).assign(
            schema=lambda _: db.get_table_info(),
            response=lambda vars: db.run(vars["query"]),
        )
        | prompt
        | openai_completion
        | StrOutputParser()
    )
    
    return chain.invoke({
        "question": user_query,
        "chat_history": chat_history,
    })

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hallo 🤖! Ich bin dein RossmAI-Chat-Assistent 😃. Fragen Sie mich einige Informationen über Ihr Kolleg."),
    ]

load_dotenv()
init_openai()  # Initialise la configuration OpenAI via Azure

#init_database(user, password,host , port , database_name)

st.set_page_config(page_title="RossmAi", page_icon=":speech_balloon:")

st.title("Chat mit RossmAi")

with st.sidebar:
    st.subheader("Settings")
    st.write("This is a simple chat application using MySQL. Connect to the database and start chatting.")
    
    st.text_input("Host", value=host, key="Host")
    st.text_input("Port", value=port, key="Port")
    st.text_input("User", value=user, key="User")
    st.text_input("Password", type='password', value="admin", key="Password")
    st.text_input("Database", value=database_name, key="Database")
    
    if st.button("Connect"):
        with st.spinner("Connecting to database..."):
            db = init_database(
                st.session_state["User"],
                st.session_state["Password"],
                st.session_state["Host"],
                st.session_state["Port"],
                st.session_state["Database"]
            )
            st.session_state.db = db
            st.success("Connected to database!")
    
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Type a message...")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))
