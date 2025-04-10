import PyPDF2
import sqlite3
from ollama import Client
import numpy as np
from numpy.linalg import norm
import os

# Add a global variable to cache the database connection and state
_db_connection = None
_data_loaded = False


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

def get_embeddings(texts, model="nomic-embed-text"):
    """Generate embeddings for a list of texts using Ollama."""
    client = Client(host='http://localhost:11434')
    embedding_response = client.embed(model=model, input=texts)
    # Debug: Print the structure of the embedding response
    # print("Embedding response structure:", embedding_response)
    return embedding_response["embeddings"]

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors, scaled to 0-100."""
    if not np.any(vec1) or not np.any(vec2) or len(vec1) != len(vec2):
        return 0.0
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2)) * 100


def initialize_sqlite_db():
    """Initialize SQLite database and create jobs table."""
    global _db_connection
    if _db_connection is None:
        _db_connection = sqlite3.connect('ats_jobs.db')
        cursor = _db_connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS jobs 
                          (id INTEGER PRIMARY KEY, job_title TEXT, job_description TEXT, embedding BLOB)''')
        _db_connection.commit()
    return _db_connection

def is_database_initialized():
    """Check if the database file exists and contains data."""
    if not os.path.exists('ats_jobs.db'):
        return False
    conn = sqlite3.connect('ats_jobs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM jobs")
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def load_jds_to_sqlite(jds_df):
    """Load job descriptions from CSV into SQLite."""
    global _data_loaded
    if _data_loaded or is_database_initialized():
        print("Job descriptions are already loaded into SQLite.")
        return

    conn = initialize_sqlite_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs")  # Clear existing data (optional)
    for index, row in jds_df.iterrows():
        embeddings = get_embeddings([row['Job Description']])
        embedding_list = embeddings[0]  # This should be a list of floats
        embedding = np.array(embedding_list, dtype=np.float32)  # Convert to NumPy array
        cursor.execute(
            "INSERT INTO jobs (job_title, job_description, embedding) VALUES (?, ?, ?)",
            (row['Job Title'], row['Job Description'], embedding.tobytes())
        )
    conn.commit()
    _data_loaded = True  # Mark data as loaded
    print(f"Loaded {len(jds_df)} job descriptions into SQLite.")

def close_sqlite_connection():
    """Close the SQLite connection."""
    global _db_connection
    if _db_connection is not None:
        _db_connection.close()
        _db_connection = None

def query_sqlite_db(resume_text, top_n=5):
    """Query SQLite for top N similar job descriptions based on resume."""
    conn = initialize_sqlite_db()
    cursor = conn.cursor()
    embeddings = get_embeddings([resume_text])
    resume_embedding_list = embeddings[0]  # Extract the first embedding
    resume_embedding = np.array(resume_embedding_list, dtype=np.float32)  # Convert to NumPy array
    
    cursor.execute("SELECT job_title, job_description, embedding FROM jobs")
    jds = cursor.fetchall()
    
    matches = []
    for jd in jds:
        jd_embedding = np.frombuffer(jd[2], dtype=np.float32)
        similarity = cosine_similarity(resume_embedding, jd_embedding)
        matches.append({
            "job_title": jd[0],
            "match_percentage": round(similarity, 2)
        })
    
    # Sort by match percentage and get top N
    matches.sort(key=lambda x: x["match_percentage"], reverse=True)
    return matches[:top_n]