# AI Codebase Investigator

A semantic code search application that helps developers find relevant code in public GitHub repositories using natural-language questions.

## Features

- Fetch source files from public GitHub repositories.
- Split source code into smaller chunks.
- Generate embeddings using Sentence Transformers.
- Search code semantically using FAISS.
- Display matching code snippets, file paths, approximate line numbers, and similarity scores.

## Tech Stack

- Python
- Streamlit
- GitHub REST API
- Sentence Transformers
- FAISS
- NumPy

## How It Works

1. The user enters a public GitHub repository URL.
2. The application fetches supported source files.
3. The source code is split into smaller chunks.
4. Sentence Transformers converts the chunks into numerical embeddings.
5. FAISS searches for chunks most similar to the user's question.
6. The application displays matching code snippets and their file locations.

## Setup Instructions

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ai-codebase-investigator
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

Enter a public GitHub repository URL and search for code using natural-language questions.

## Current Limitations

- This version performs semantic code search; it does not generate LLM explanations or automatically diagnose bugs.
- Private repository authentication is not implemented.
- Search quality depends on the retrieved code chunks.
- The application supports a limited set of programming-language file extensions.

## Future Improvements

- Add LLM-powered code explanations.
- Improve repository indexing and caching.
- Support private repositories securely.
- Add automated tests and more detailed code references.

## Security

Never commit API keys, passwords, access tokens, or other secrets to the repository.
