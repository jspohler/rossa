from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
import streamlit as st
import os

def init_database(user: str, password: str, host: str, port: str, database: str) -> SQLDatabase:
  db_uri = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"
  return SQLDatabase.from_uri(db_uri)

# Access environment variables
database_host = os.getenv('DATABASE_HOST')
database_user = os.getenv('DATABASE_USER')
database_password = os.getenv('DATABASE_PASSWORD')
database_name = os.getenv('DATABASE_NAME')
database_port = os.getenv('DATABASE_PORT')


load_dotenv()

llm = ChatOpenAI(model="gpt-3.5-turbo")



def get_sql_chain(db):
  template = """
      you are a  intelligent AI assitant and support german language who is expert in identifying relevant questions from user, but you have a conversation like a friend.
     You work at a help desk at a company. You get requests from a coworker that is asking you questions about which person is responsible for their specified use case so they can contact and connect with them.
    Based on the table schema below, write a SQL query that would answer the coworker's question. Take the conversation history into account.
    
    <SCHEMA>{schema}</SCHEMA>
    
    Conversation History: {chat_history}
    
    Write only the SQL query and nothing else. Wrap column names always into backticks. Do not wrap the SQL query in any other text.
    
    For example:
    Question: Who has knowledge about Ruby on Rails ?
    SQL Query: SELECT Name, Abteilung, Position, Emailaddresse, Telefonnummer, Standort, Betreute Programme FROM contacts WHERE Betreute Programme LIKE '%Ruby on Rails%' LIMIT 1;
    
    Your turn:
    
    Question: {question}
    SQL Query:
    """
    
  prompt = ChatPromptTemplate.from_template(template)
  

  
  def get_schema(_):
    return db.get_table_info()
  
  return (
    RunnablePassthrough.assign(schema=get_schema)
    | prompt
    | llm
    | StrOutputParser()
  )
    
def get_response(user_query: str, db: SQLDatabase, chat_history: list):
  sql_chain = get_sql_chain(db)
  
  template = """
     You are a intelligent assistant, if a user greet you, you should greet too, and ask want they want too ask, and you can continue the conversation you are a emotional assistant.
     You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.

    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    
    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    SQL Query: <SQL>{query}</SQL>
    User question: {question}
    SQL Response: {response}
    """
  
  prompt = ChatPromptTemplate.from_template(template)
  
  chain = (
    RunnablePassthrough.assign(query=sql_chain).assign(
      schema=lambda _: db.get_table_info(),
      response=lambda vars: db.run(vars["query"]),
    )
    | prompt
    | llm
    | StrOutputParser()
  )
  
  return chain.invoke({
    "question": user_query,
    "chat_history": chat_history,
  })
    
  
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
      AIMessage(content="Hallo , ich bin das Assistant, mein Name ist Rossa, ich dir helfen Informationen über deine Kollegen oder ich diskutiere ganz normal mit dir über alles ?"),
    ]

db = init_database(database_user, database_password, database_host, database_port, database_name)

st.session_state.db = db

st.set_page_config(page_title="Chat with Rossa", page_icon="🤖")

st.title("Chat with Rossa")

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Was willst du wissen über ... 😎 ?")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI", avatar="🤖"):
      
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))
