# Import the 'os' module to interact with the operating system 
# (e.g., handling file paths, reading environment variables).
import os

# Import 'shutil' for high-level file operations, such as copying 
# and moving files (likely used here to save uploaded files to disk).
import shutil

# Import necessary components from FastAPI to build the web API.
# FastAPI: The main class to create the API application.
# UploadFile & File: Classes to handle file uploads in API endpoints.
# HTTPException: Used to raise HTTP errors (e.g., 400 Bad Request, 404 Not Found).
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware 

# Import BaseModel from Pydantic to define data schemas and perform 
# request body validation (e.g., validating JSON inputs).
from pydantic import BaseModel

# Import load_dotenv to read key-value pairs from a .env file and 
# set them as environment variables (useful for API keys and config).
from dotenv import load_dotenv

# --- LangChain & AI Tools ---

# Import PyPDFLoader to load and extract text from PDF files.
# This is part of the document processing pipeline.
from langchain_community.document_loaders import PyPDFLoader

# Import RecursiveCharacterTextSplitter to split large texts into smaller chunks.
# This is crucial for RAG (Retrieval-Augmented Generation) to fit text 
# within the model's context window.
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import HuggingFaceEmbeddings to convert text chunks into vector embeddings 
# using models from Hugging Face (open-source models).
from langchain_huggingface import HuggingFaceEmbeddings

# Import Chroma, a vector store database, to store the generated embeddings 
# and perform similarity searches for retrieval.
from langchain_chroma import Chroma

# Import ChatGroq to interface with Groq's API, which provides access 
# to fast LLM inference (e.g., Llama 3, Mixtral).
from langchain_groq import ChatGroq

# Import RetrievalQA, a pre-built chain that combines a retriever 
# (fetching relevant docs) with an LLM (answering questions based on those docs).
from langchain.chains import RetrievalQA


# Load environment variables (like API keys) from a .env file into the system.
# This ensures sensitive data isn't hardcoded in the script.
load_dotenv()

# Create an instance of the FastAPI application.
# This 'app' object will define routes (endpoints) and handle incoming web requests.
app = FastAPI()


# --- middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, we'd specify "http://localhost:5173"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the directory path where uploaded files will be stored.
UPLOAD_DIR = "uploads"

# Create the upload directory if it doesn't already exist.
# exist_ok=True prevents an error if the folder is already there.
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Initialize the Embedding Model.
# This downloads/loads a specific pre-trained model ("all-MiniLM-L6-v2") from Hugging Face.
# This model converts text (sentences/chunks) into numerical vectors (lists of numbers)
# so the computer can understand semantic similarity.
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


# Initialize the Vector Database (Chroma).
# This acts as the "long-term memory" for the application.
# - collection_name: A label to organize this specific set of data.
# - embedding_function: Uses the model defined above to vectorize data before storing.
# - persist_directory: Saves the database to a local folder ("./chroma_db") so data
#   isn't lost when the program restarts.
vector_store = Chroma(
    collection_name="pdf_chat",
    embedding_function=embedding_model,
    persist_directory="./chroma_db"
)

# Initialize the Large Language Model (Groq).
# This acts as the "brain" that generates natural language responses.
# - temperature=0: Sets the creativity to the lowest level for factual, consistent answers.
# - model_name: Specifies the model version (Llama 3 8B) optimized for speed.
# - api_key: Authenticates with the Groq service using the key loaded from .env.
llm = ChatGroq(
    temperature=0,
    model_name="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY") 
)


# --- Request Models ---

# Define a Pydantic model for the chat endpoint.
# This ensures that the incoming JSON body must have a "question" field 
# and that it is a string. If not, FastAPI validates it and returns an error automatically.
class QuestionRequest(BaseModel):
    question: str 

# --- API Endpoints ---

# A simple "Health Check" endpoint. 

@app.get("/")
def read_root():
    return {"message": "Talk with PDF Backend (Groq Edition) is running!"}


# The Upload Endpoint: This is the "Ingestion" phase of RAG.
# It takes a PDF, processes it, and saves the knowledge into the vector database.
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """ 
    Ingests a pdf: upload -> save -> split -> embed -> store in ChromaDB
    """
    
    # a. Save the uploaded file to disk.
    # We read the incoming file stream and write it to the "uploads" folder 
    # so the document loader can access it physically.
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # b. Load and Split the document.
    # - PyPDFLoader reads the text from the PDF.
    # - RecursiveCharacterTextSplitter breaks the long text into smaller "chunks" (1000 chars).
    #   Why? LLMs have a limit on how much text they can read at once, and 
    #   searching small specific chunks is more accurate than searching whole books.
    # - chunk_overlap=200 ensures sentences aren't cut in half awkwardly at the edges.
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    # c. Store in Vector DB (Chroma).
    # This takes the text chunks, runs them through the embedding model (to turn text into numbers),
    # and saves them into the 'vector_store'. 
    vector_store.add_documents(chunks)
    
    return {"filename": file.filename, "chunks": len(chunks), "status": "Learned"}


# The Chat Endpoint: This is the "Retrieval & Generation" phase.
# It receives a question, finds relevant data in the DB, and generates an answer.
@app.post("/chat")
async def chat_with_pdf(request: QuestionRequest):
    """
    The RAG pipeline: Question -> Vector Search -> Groq Answer
    """
    
    # a. Create the Retrieval Chain.
    # - RetrievalQA connects the LLM (Groq) with the Vector Store (Chroma).
    # - search_kwargs={"k": 3}: It will find the top 3 most relevant chunks from the PDF.
    # - return_source_documents=True: It will return the chunks it used so we can cite sources.
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )

    # b. Ask the question.
    # The chain automatically:
    # 1. Embeds the user's question.
    # 2. Searches the DB for similar chunks.
    # 3. Sends the question + those chunks to Groq to generate an English answer.
    result = qa_chain.invoke({"query": request.question})

    # c. Return the answer and sources.
    # We return the AI's answer and a snippet (first 100 chars) of the source text
    # so the user knows where the info came from.
    return {
        "answer": result["result"],
        "sources": [doc.page_content[:500] + "..." for doc in result["source_documents"]]
    }