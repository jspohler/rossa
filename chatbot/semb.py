
import streamlit as st
from embedding_manager import get_choised_vector
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from const import *

load_dotenv()

llm = ChatOpenAI() #LLM GPT-3.5 Turbo



def get_context_retriever_chain(vector_store):
    
    retriever = vector_store.as_retriever()
    
    prompt = ChatPromptTemplate.from_messages([
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}"),
      ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
    ])
    
    retriever_chain = create_history_aware_retriever(llm, retriever, prompt)
    
    return retriever_chain
    
def get_conversational_rag_chain(retriever_chain): 
    prompt = ChatPromptTemplate.from_messages([
      ("system", "Answer the user's questions based only on the below context:\n\n{context} if you find the information on the below context, say that you dont have the answer, and you can ask for more detail to the user to have more information about it question."),
      MessagesPlaceholder(variable_name="chat_history"),
      ("user", "{input}"),
    ])
    stuff_documents_chain = create_stuff_documents_chain(llm,prompt)
    return create_retrieval_chain(retriever_chain, stuff_documents_chain)

def get_response(user_input):
    retriever_chain = get_context_retriever_chain(st.session_state.vector_store)
    conversation_rag_chain = get_conversational_rag_chain(retriever_chain)
    
    response = conversation_rag_chain.invoke({
        "chat_history": st.session_state.chat_history,
        "input": user_input
    })
    
    return response['answer']

pdf_files = list_pdf_files(pdf_directory)

def app():

    st.set_page_config(page_title="Dein HsB Chatbot", page_icon="💬")
    # app config
    st.title("Dein HsB Chatbot.")

     #sidebar
    with st.sidebar:
        st.header("Einstellungen")
        # Use sidebar for embedding selection and dropdown
        embedding_type = st.sidebar.radio(
            "Wählen Sie den Embedding model:",
            (prototypA, prototypB) # Prototyp A für openai & Prototyp B für bge-m3
        )
    
     # Check if embedding_type has changed, reset chat if it has
    if 'previous_embedding_type' not in st.session_state:
        st.session_state.previous_embedding_type = embedding_type
    elif embedding_type != st.session_state.previous_embedding_type:
        st.session_state.chat_history = [
            AIMessage(content="Hallo, Ich bin das HSB Chatbot. Wie kann dir helfen?"),
        ]
        st.session_state.previous_embedding_type = embedding_type
    
    st.sidebar.write("Datenquellen: ")
    st.sidebar.text('Die folgende URLs stammen alle aus der Webseite der Hs Bremen.')
    #st.sidebar.write(data_origin)
    texts = [
       # "-   ",
        "- Die folgende Modulbeschreibungen von jeden Studiengänge der Fakultät 4:",
        " ",
    ]

    texts.extend(pdf_files)

     # Display each text in the list
    text_to_display = "\n".join(texts)

  

    # Display the text area with a scrollbar
    st.sidebar.text_area("Modulhandbücher", text_to_display, height=150, disabled=True)

    st.sidebar.write('Studiengänge :')
    st.sidebar.write("https://www.hs-bremen.de/die-hsb/fakultaeten/elektrotechnik-und-informatik/")
    

    # session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hallo, Ich bin das HSB Chatbot. Wie kann dir helfen?"),
        ]
   
    st.session_state.vector_store = get_choised_vector(embedding_type=embedding_type)


    # user input
    user_query = st.chat_input("Schreiben ihre Nachricht hier...")
    if user_query is not None and user_query != "":
        response = get_response(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))
        

    # conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)
            
if __name__ == '__main__':
    app()