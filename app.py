from flask import Flask, render_template, jsonify, request
from src.helper import download_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain,create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from src.prompt import *
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import os


app = Flask(__name__)


#Environment Setup
load_dotenv()
PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


embeddings = download_embeddings()
index_name = "medical-chatbot"

# Load Existing Index
# Embed each chunk and upsert the embeddings into your Pinecode index.
docsearch = PineconeVectorStore.from_existing_index(
    embedding=embeddings,
    index_name= index_name
)


retriver = docsearch.as_retriever(search_type="similarity", search_kwargs={"k":3})


# Initialize the LLM
chatmodel = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=1.0,  # Gemini 3.0+ defaults to 1.0
    max_tokens=None,
    timeout=None,
    max_retries=2,

)

#Prompt to rephrase follow-up questions using history
condense_prompt = ChatPromptTemplate.from_messages([
    ("system", condense_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

#History-aware retriever (rewrites question before searching)
history_aware_retriever = create_history_aware_retriever(
    chatmodel,
    retriver,
    condense_prompt
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ]
)

#Prompt for answering using retrieved docs 
question_answer_chain = create_stuff_documents_chain(chatmodel, prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# Store for all sessions
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chain_with_memory = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer"
)



@app.route("/")
def index():
    return render_template('chat.html')



@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]
    print(input)
    response = chain_with_memory.invoke({"input": msg}, config={"configurable": {"session_id": "user_1"}})
    print("Response : ", response["answer"])
    return str(response["answer"])




if __name__ == '__main__':    app.run(host="0.0.0.0", port= 8080, debug= True)