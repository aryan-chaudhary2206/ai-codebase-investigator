import requests
import streamlit as st
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

st.set_page_config(page_title="AI Codebase Investigator", page_icon="🔎")
st.title("🔎 AI Codebase Investigator")
st.write("Search a GitHub repository by the meaning of your question.")

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def fetch_files(owner, repo, path=""):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    items = response.json()

    files = []
    for item in items:
        if item["type"] == "file" and item["name"].endswith(
            (".py", ".js", ".ts", ".java", ".cpp", ".c", ".go", ".rs")
        ):
            if item.get("size", 0) <= 300_000:
                raw = requests.get(item["download_url"], timeout=20)
                if raw.ok:
                    files.append({
                        "path": item["path"],
                        "content": raw.text
                    })
        elif item["type"] == "dir" and item["name"] not in {
            ".git", "node_modules", "venv", ".venv", "__pycache__"
        }:
            files.extend(fetch_files(owner, repo, item["path"]))
        if len(files) >= 150:
            break
    return files[:150]

def make_chunks(files, max_lines=40):
    chunks = []
    for file in files:
        lines = file["content"].splitlines()
        for start in range(0, len(lines), max_lines - 5):
            text = "\n".join(lines[start:start + max_lines])
            if text.strip():
                chunks.append({
                    "path": file["path"],
                    "start_line": start + 1,
                    "code": text
                })
    return chunks

@st.cache_resource
def build_index(chunk_texts):
    model = load_model()
    vectors = model.encode(chunk_texts, normalize_embeddings=True)
    vectors = np.asarray(vectors, dtype="float32")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index

with st.form("repo_form"):
    repo_url = st.text_input(
        "Public GitHub repository URL",
        placeholder="https://github.com/owner/repository"
    )
    submitted = st.form_submit_button("Load repository")

if submitted:
    try:
        parts = repo_url.strip("/").split("/")
        if len(parts) < 5 or parts[2] != "github.com":
            st.error("Enter a URL like https://github.com/owner/repository")
            st.stop()

        owner, repo = parts[3], parts[4].removesuffix(".git")
        with st.spinner("Fetching repository source files..."):
            files = fetch_files(owner, repo)

        if not files:
            st.error("No supported source files were found.")
            st.stop()

        chunks = make_chunks(files)
        texts = [
            f"File: {c['path']}\nCode:\n{c['code']}"
            for c in chunks
        ]

        with st.spinner("Creating semantic search index..."):
            index = build_index(tuple(texts))

        st.session_state["chunks"] = chunks
        st.session_state["texts"] = texts
        st.session_state["index"] = index
        st.session_state["repo"] = f"{owner}/{repo}"
        st.success(
            f"Indexed {len(files)} files into {len(chunks)} code chunks."
        )
    except Exception as error:
        st.error(f"Could not load repository: {error}")

if "index" in st.session_state:
    st.subheader(f"Repository: {st.session_state['repo']}")
    question = st.text_input(
        "What do you want to find?",
        placeholder="Where is password validation implemented?"
    )

    if st.button("Search code") and question.strip():
        model = load_model()
        query = model.encode(
            [question], normalize_embeddings=True
        ).astype("float32")
        scores, indices = st.session_state["index"].search(query, 5)

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            chunk = st.session_state["chunks"][int(idx)]
            st.markdown(
                f"**{chunk['path']} — around line {chunk['start_line']}**"
            )
            st.caption(f"Similarity score: {float(score):.3f}")
            st.code(chunk["code"], language="python")
