# TalkWithPDF: RAG-Powered Document Assistant

![Project Status](https://img.shields.io/badge/Status-Live-success)
![Stack](https://img.shields.io/badge/Stack-FastAPI_React_Groq-blue)
![Deployment](https://img.shields.io/badge/Deploy-Docker_Vercel-orange)

A high-performance, full-stack AI application that allows users to chat with their PDF documents. Built with a decoupled architecture using **FastAPI** (Python) for the RAG pipeline and **React** (Vite) for the frontend.

**[🚀 View Live Demo](https://chatwithpdf-git-main-anjil-adhikaris-projects.vercel.app/)**

---

## 🏗 Architecture

The application follows a decoupled client-server architecture to ensure scalability and separation of concerns.

### The Stack
* **Frontend:** React + Vite + Tailwind CSS (Deployed on Vercel).
* **Backend:** FastAPI + Uvicorn (Containerized with Docker on Hugging Face Spaces).
* **AI Inference (LLM):** Llama-3-8b via **Groq LPU** (Language Processing Unit) for ultra-low latency.
* **Vector Store:** ChromaDB (In-memory) for efficient similarity search.
* **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (Running locally for zero-cost embedding).

### The RAG Pipeline (Retrieval-Augmented Generation)
1.  **Ingestion:** User uploads a PDF.
2.  **Chunking:** Text is split into 1000-character chunks (with overlap) to preserve context.
3.  **Embedding:** Chunks are converted into vector embeddings using HuggingFace.
4.  **Storage:** Vectors are stored in a transient ChromaDB instance.
5.  **Retrieval:** User queries are converted to vectors; the system retrieves the top 3 most relevant chunks.
6.  **Generation:** The relevant context + user query is sent to **Llama 3 (Groq)** to generate a precise answer.

---

## 🚀 Features

* **⚡ Ultra-Fast Inference:** Leverages Groq's LPU technology for near-instant AI responses.
* **📄 PDF Parsing:** Robust text extraction handling various PDF formats.
* **🧠 Contextual Awareness:** Uses similarity search to "read" only the relevant parts of the document.
* **🐳 Dockerized:** Fully containerized backend for consistent deployment across environments.
* **🎨 Modern UI:** Clean, split-screen interface built with Tailwind CSS.

---

## 🛠 Local Setup

### Prerequisites
* Node.js & npm
* Python 3.9+
* Groq API Key (Get one [here](https://console.groq.com/keys))

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=gsk_your_key_here" > .env

# Run Server
uvicorn main:app --reload