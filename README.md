# TalkWithPDF: RAG-Powered Document Assistant

![Project Status](https://img.shields.io/badge/Status-Live-success)
![Stack](https://img.shields.io/badge/Stack-FastAPI_React_Groq-blue)
![Deployment](https://img.shields.io/badge/Deploy-Docker_Vercel-orange)

A high-performance, full-stack AI application that allows users to chat with their PDF documents. Built with a decoupled architecture using **FastAPI** (Python) for the RAG pipeline and **React** (Vite) for the frontend.

**[ View Live Demo](https://chatwithpdf-git-main-anjil-adhikaris-projects.vercel.app/)**

---

##  Architecture

The application follows a decoupled client-server architecture to ensure scalability and separation of concerns.

### The Stack
* **Frontend:** React + Vite + Tailwind CSS.
* **Backend:** FastAPI + Uvicorn.
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

## ☁️ Deployment

This project is deployed using a modern, cloud-native approach:

### 1. Backend: Hugging Face Spaces (Docker)
The FastAPI backend is containerized using **Docker** and hosted on **Hugging Face Spaces**.
* **Why:** Hugging Face provides a generous free tier with 16GB RAM, which is critical for running the local embedding model (`all-MiniLM-L6-v2`) and ChromaDB in-memory without crashing.
* **URL:** `https://anjil-talk-with-pdf.hf.space`

### 2. Frontend: Vercel
The React frontend is deployed on **Vercel**, utilizing their Edge Network for fast global access.
* **Why:** Native support for Vite/React and seamless CI/CD integration with GitHub.
* **Configuration:** Deployed as a monorepo with the Root Directory set to `frontend`.
* **URL:** [https://chatwithpdf-git-main-anjil-adhikaris-projects.vercel.app/](https://chatwithpdf-git-main-anjil-adhikaris-projects.vercel.app/)

---

## Features

* **⚡ Ultra-Fast Inference:** Leverages Groq's LPU technology for near-instant AI responses.
* ** PDF Parsing:** Robust text extraction handling various PDF formats.
* ** Contextual Awareness:** Uses similarity search to "read" only the relevant parts of the document.
* ** Dockerized:** Fully containerized backend for consistent deployment across environments.
* ** Modern UI:** Clean, split-screen interface built with Tailwind CSS.

---

##  Local Setup

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