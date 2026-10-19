# Sanskrit & Bhagavad Gita Learning Chatbot 🕉️

A Python and Streamlit chatbot designed for learning Sanskrit vocabulary, grammar, and exploring the Bhagavad Gita through retrieved authentic verses.

---

## Features (Stage by Stage)

- **Stage 1 (Current)**:
  - Streamlit chat interface with rich aesthetics, Devanagari styling, and chat history.
  - Pluggable LLM client wrapper (`llm_client.py`) supporting Google Gemini, OpenAI, and Groq via environment variables.
  - Strict system prompt enforcing 3-part replies: **Devanagari**, **IAST**, and **English Meaning**.
- **Stage 2**: Input transliteration and script detection (Devanagari, IAST, Harvard-Kyoto, ITRANS).
- **Stage 3**: Sanskrit-English dictionary lookups (Monier-Williams SQLite) and Paninian morphology/sandhi analysis.
- **Stage 4**: RAG over authentic Bhagavad Gita verses using ChromaDB and multilingual embeddings.
- **Stage 5**: 30-question evaluation benchmark measuring retrieval precision and citation adherence.

---

## Getting Started

### 1. Prerequisites
- Python 3.11+
- Virtual environment tool (`venv`)

### 2. Virtual Environment Setup

```powershell
# Navigate into the project folder
cd sanskrit-bot

# Create virtual environment (if not already created)
python -m venv .venv

# Activate virtual environment
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```

Edit `.env` and set your preferred provider and API key:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_key
```

### 4. Running the Application

```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.
