from langchain_community.llms import Ollama
from utils.helpers import get_embeddings, save_to_sqlite
import json

ollama_model = Ollama(base_url='http://localhost:11434', model='ats_model')

class ExtractorAgent:
    def process(self, input_text):
        return ollama_model.invoke(f"Extract keywords from: {input_text}")

class ComparatorAgent:
    def process(self, jd_keywords, resume_keywords):
        prompt = f"Compare keywords: JD-{jd_keywords}, Resume-{resume_keywords}. Return JSON with 'keywords': [], 'mismatches': [], 'score': int."
        return ollama_model.invoke(prompt)

def analyze_jd_resume(job_desc, resume_text):
    # Extract keywords
    jd_keywords = ExtractorAgent().process(job_desc)
    resume_keywords = ExtractorAgent().process(resume_text)
    
    # Compare and get score
    response = ComparatorAgent().process(jd_keywords, resume_keywords)
    result = json.loads(response)
    
    # Save to SQLite
    save_to_sqlite(job_desc, resume_text, response)
    
    # Generate embeddings (optional)
    embeddings = get_embeddings([job_desc, resume_text])
    return result, embeddings