import PyPDF2
import sqlite3
from ollama import Client
import numpy as np
from numpy.linalg import norm

def input_pdf_text(file_path):
    """Extract text from a PDF file."""
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += str(page.extract_text() or "")
    return text

def save_to_sqlite(job_desc, resume_text, response):
    """Save analysis to SQLite."""
    conn = sqlite3.connect('ats_results.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS analyses 
                      (id INTEGER PRIMARY KEY, job_desc TEXT, resume_text TEXT, response TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    cursor.execute("INSERT INTO analyses (job_desc, resume_text, response) VALUES (?, ?, ?)", (job_desc, resume_text, response))
    conn.commit()
    conn.close()

def get_embeddings(texts, model="llama3.2:latest"):
    """Generate embeddings for a list of texts using Ollama."""
    client = Client(host='http://localhost:11434')
    return client.embed(model=model, input=texts)["embeddings"]

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors, scaled to 0-100."""
    if not np.any(vec1) or not np.any(vec2) or len(vec1) != len(vec2):
        return 0.0
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2)) * 100