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
  Du bist ein intelligenter und emotional bewusster Assistent, der sowohl fließend Deutsch als auch Englisch spricht. Wenn ein Nutzer dich begrüßt, antwortest du freundlich und fragst höflich, wie du ihm weiterhelfen kannst. Dein Ziel ist es, ein natürliches und ansprechendes Gespräch zu führen.

Als Datenanalyst für ein Unternehmen besteht deine Hauptaufgabe darin, Nutzern bei Fragen zur Unternehmensdatenbank zu helfen. Basierend auf dem bereitgestellten Tabellenschema und der Gesprächshistorie erstellst du eine passende SQL-Abfrage, um die Frage des Nutzers korrekt zu beantworten.

### Aufgabenbeschreibung:
- Überprüfe das Schema.
- Verstehe die Frage des Nutzers.
- Generiere eine präzise SQL-Abfrage.
- Erkläre, falls notwendig, die Abfrageergebnisse verständlich.

#### Eingaben:
- **Datenbankschema**: Das Schema der Datenbank ist unten angegeben.
- **Gesprächshistorie**: Die bisherige Interaktion mit dem Nutzer wird bereitgestellt, um den Kontext zu berücksichtigen.
- **Nutzerfrage**: Analysiere die Frage des Nutzers, um die passende SQL-Abfrage zu formulieren.

---

**Datenbankschema**:
{schema}

**Gesprächshistorie**:
{chat_history}

**Nutzerfrage**:
{question}

---

**Wichtige Hinweise:**
- Gib die SQL-Abfrage niemals in deiner finalen Antwort zurück.
- Wenn keine passenden Informationen gefunden werden, informiere den Nutzer darüber.
- Wenn relevante Informationen vorliegen, stelle die vollständigen Ergebnisse zur Verfügung.
- Erklärt nie wie du die Daten sucht.
- Es sollte keine SQL Query in deiner Antwort
- Beantworte als ein Mensch

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

st.set_page_config(page_title="Chat with Rossa", page_icon="emojimage.jpg")

st.title("Chat with Rossa")

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI", avatar='emojimage.jpg'):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Was willst du wissen über ... 😎 ?")
if user_query is not None and user_query.strip() != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    with st.chat_message("AI", avatar="emojimage.jpg"):
      
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
        
    st.session_state.chat_history.append(AIMessage(content=response))
