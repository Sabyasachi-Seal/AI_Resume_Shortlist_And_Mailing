import pandas as pd
import os
from src.processor import ATSProcessor
from utils.helpers import input_pdf_text
import tempfile

def test_core():
    # Load JDs from CSV
    jds_path = "./data/jds.csv"
    if not os.path.exists(jds_path):
        print(f"Error: {jds_path} not found. Please ensure the file exists.")
        return
    
    jds_df = pd.read_csv(jds_path, encoding="ISO-8859-1")
    if jds_df.empty:
        print("Error: jds.csv is empty or invalid.")
        return

    # Select a sample job title (first one for testing)
    sample_job_title = jds_df['Job Title'].iloc[0]
    job_desc = jds_df[jds_df['Job Title'] == sample_job_title]['Job Description'].iloc[0]
    print(f"Testing with Job Title: {sample_job_title}")
    print(f"Job Description: {job_desc[:200]}...")  # Print first 200 chars

    # Process a sample resume from /data/resumes/
    resumes_dir = "./data/resume/"
    if not os.path.exists(resumes_dir):
        print(f"Error: {resumes_dir} not found. Please add resume PDFs to this directory.")
        return

    resume_files = [f for f in os.listdir(resumes_dir) if f.endswith('.pdf')]
    if not resume_files:
        print(f"Error: No PDF files found in {resumes_dir}.")
        return

    sample_resume_file = os.path.join(resumes_dir, resume_files[0])
    print(f"Using Resume: {sample_resume_file}")

    # Extract text from the resume
    with open(sample_resume_file, "rb") as f:
        resume_data = f.read()
        resume_path = os.path.join(tempfile.gettempdir(), sample_resume_file.split('/')[-1])
        with open(resume_path, "wb") as temp_f:
            temp_f.write(resume_data)
        resume_text = input_pdf_text(resume_path)

    print(f"Resume Text (first 200 chars): {resume_text[:200]}...")

    # Test the processor
    try:
        processor = ATSProcessor()
        result = processor.analyze(job_desc, resume_text)
        print("\nAnalysis Result:")
        print(result)
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    test_core()