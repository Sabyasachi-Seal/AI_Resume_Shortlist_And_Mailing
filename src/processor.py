from langchain_ollama import OllamaLLM
from utils.helpers import save_to_sqlite, query_sqlite_db, load_jds_to_sqlite
import pandas as pd
import os
import json

class ATSVectorProcessor:
    def __init__(self, top_n=5):
        try:
            self.top_n = top_n
            # Load JDs into SQLite on initialization (one-time setup)
            jds_path = "./data/jds.csv"
            if os.path.exists(jds_path):
                jds_df = pd.read_csv(jds_path, encoding="ISO-8859-1")
                if not jds_df.empty:
                    load_jds_to_sqlite(jds_df)
                else:
                    print("Warning: jds.csv is empty or invalid.")
            else:
                print(f"Warning: {jds_path} not found. SQLite will not be populated.")
        except Exception as e:
            raise Exception(f"Error initializing vector processor: {e}")

    def analyze(self, resume_text):
        """Analyze resume and return top N matching job titles with percentages."""
        try:
            # Query SQLite for top N matches
            matches = query_sqlite_db(resume_text, self.top_n)

            return matches
        except Exception as e:
            return {"error": str(e)}