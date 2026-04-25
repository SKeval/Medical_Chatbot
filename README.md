# 🏥 Medical Chatbot — RAG-Powered Clinical Q&A Assistant

> A production-grade conversational AI for medical knowledge retrieval, built with **LangChain**, **Pinecone**, **Google Gemini**, **Flask**, and deployed on **AWS** via Docker.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green?style=flat-square)
![Pinecone](https://img.shields.io/badge/Pinecone-VectorDB-purple?style=flat-square)
![Gemini](https://img.shields.io/badge/Google-Gemini-orange?style=flat-square&logo=google)
![Flask](https://img.shields.io/badge/Flask-Web%20API-lightgrey?style=flat-square&logo=flask)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=flat-square&logo=docker)
![AWS](https://img.shields.io/badge/AWS-CI%2FCD-yellow?style=flat-square&logo=amazon-aws)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📌 Overview

The **Medical Chatbot** is an end-to-end Retrieval-Augmented Generation (RAG) system that allows users to ask natural-language medical questions and receive contextually accurate answers grounded in a curated corpus of medical PDFs.

Unlike simple FAQ bots, this system supports **multi-turn conversations** with full history awareness — it rephrases follow-up questions in context before searching, making interactions feel natural and coherent.

---

## ✨ Key Features

- 🔍 **RAG Pipeline** - PDF ingestion → chunking → embedding → Pinecone vector search → Gemini generation
- 🧠 **Conversation Memory** - `InMemoryChatMessageHistory` preserves session context across turns
- 🔄 **History-Aware Retrieval** - LangChain rephrases follow-up questions before semantic search
- ⚡ **Gemini LLM** - Powered by `gemini-3-flash-preview` for fast, high-quality medical responses
- 📦 **Pinecone Serverless** - 384-dim cosine-similarity index on AWS `us-east-1`
- 🌐 **Flask REST API** - Lightweight web interface with real-time chat UI
- 🐳 **Docker + CI/CD** - Containerized and auto-deployed to AWS via GitHub Actions

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION                              │
│                                                                     │
│  Medical PDFs  ──►  PyPDF Loader  ──►  Text Splitter  ──►          │
│  HuggingFace Embeddings (384-dim)  ──►  Pinecone Index             │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        INFERENCE PIPELINE                           │
│                                                                     │
│  User Query                                                         │
│      │                                                              │
│      ▼                                                              │
│  Chat History  ──►  Condense Prompt  ──►  Gemini (rephrase)        │
│                                               │                     │
│                                               ▼                     │
│                              Pinecone Similarity Search (k=3)       │
│                                               │                     │
│                                               ▼                     │
│                    Retrieved Docs  ──►  Gemini Generation           │
│                                               │                     │
│                                               ▼                     │
│                                         Final Answer                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| LLM | Google Gemini (`gemini-3-flash-preview`) |
| Embeddings | HuggingFace `sentence-transformers` (384-dim) |
| Vector Store | Pinecone Serverless (cosine, AWS us-east-1) |
| RAG Framework | LangChain (`langchain-classic`, `langchain-pinecone`) |
| Web Server | Flask |
| Containerization | Docker |
| CI/CD & Cloud | GitHub Actions + AWS |
| Data Ingestion | PyPDF + LangChain Text Splitter |

---

## 📁 Project Structure

```
Medical_Chatbot/
├── .github/
│   └── workflows/          # CI/CD pipeline (GitHub Actions → AWS)
├── data/                   # Medical PDF corpus
├── research/               # Experimentation notebooks
├── src/
│   ├── helper.py           # PDF loading, embedding, chunking utilities
│   └── prompt.py           # System & condense prompt templates
├── static/                 # Frontend assets (CSS, JS)
├── templates/
│   └── chat.html           # Flask chat UI
├── app.py                  # Main Flask application & RAG chain
├── store_index.py          # One-time Pinecone index creation & ingestion
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
└── setup.py                # Package setup
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker (for containerized deployment)
- A [Pinecone](https://www.pinecone.io/) account
- A [Google AI Studio](https://aistudio.google.com/) API key (Gemini)

### 1. Clone the Repository

```bash
git clone https://github.com/SKeval/Medical_Chatbot.git
cd Medical_Chatbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
PINECONE_API_KEY=your_pinecone_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 4. Ingest Medical Documents

Place your PDF files in the `data/` folder, then run the indexing script:

```bash
python store_index.py
```

This will:
- Load and parse all PDFs
- Split text into chunks
- Generate HuggingFace embeddings
- Create and populate a Pinecone serverless index named `medical-chatbot`

### 5. Run the Application

```bash
python app.py
```

Visit `http://localhost:8080` to start chatting.

### 6. Run with Docker

```bash
docker build -t medical-chatbot .
docker run -p 8080:8080 --env-file .env medical-chatbot
```

---

## 🔁 RAG Chain Detail

The system uses a **two-stage LangChain chain**:

1. **History-Aware Retriever** — Given the conversation history and a new user question, Gemini first rephrases the question into a standalone query (resolving pronouns and context). This rewritten query is then used for Pinecone similarity search.

2. **Stuff Documents Chain** — The top-3 retrieved document chunks are injected into a system prompt alongside the full chat history, and Gemini generates the final grounded answer.

Memory is maintained per session using `InMemoryChatMessageHistory` via `RunnableWithMessageHistory`.

---

## ☁️ Deployment

The project includes a GitHub Actions CI/CD pipeline that:
1. Builds a Docker image on every push to `main`
2. Pushes the image to AWS ECR
3. Deploys to AWS (EC2 / ECS)

Configure the following GitHub Secrets for deployment:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `PINECONE_API_KEY`
- `GEMINI_API_KEY`

---

## 🧪 Research & Experiments

The `research/` folder contains Jupyter notebooks used during development, including embedding experiments, prompt engineering iterations, and retrieval quality evaluations.

---

## 🔮 Future Improvements

- [ ] Add user authentication and persistent per-user session storage
- [ ] Evaluate and benchmark retrieval quality (MRR, NDCG)
- [ ] Support multi-document source citations in responses
- [ ] Add streaming responses for better UX
- [ ] Integrate medical ontologies (SNOMED CT, ICD-10) for entity-aware retrieval
- [ ] Expand language support (multilingual embeddings)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 Author

**SKeval** — [GitHub Profile](https://github.com/SKeval)

*If you found this project useful, please consider giving it a ⭐!*
