import os
from src.processor import ATSVectorProcessor
from utils.helpers import input_pdf_text
import tempfile

def test_core():
    # Process a sample resume from /data/resumes/
    resumes_dir = "./data/resume/"
    if not os.path.exists(resumes_dir):
        print(f"Error: {resumes_dir} not found. Please add resume PDFs to this directory.")
        return

    resume_files = [f for f in os.listdir(resumes_dir) if f.endswith('.pdf')]
    if not resume_files:
        print(f"Error: No PDF files found in {resumes_dir}.")
        return

    sample_resume_file = os.path.join(resumes_dir, resume_files[11])
    print(f"Using Resume: {sample_resume_file}")

    # Extract text from the resume
    with open(sample_resume_file, "rb") as f:
        resume_data = f.read()
        resume_path = os.path.join(tempfile.gettempdir(), sample_resume_file.split('/')[-1])
        with open(resume_path, "wb") as temp_f:
            temp_f.write(resume_data)
        resume_text = input_pdf_text(resume_path)

    print(f"Resume Text (first 200 chars): {resume_text[:200]}...")

    try:
        processor = ATSVectorProcessor(top_n=3)  # Adjust top_n as needed
        matches = processor.analyze(resume_text)
        print("\nTop Matching Job Titles:")

        for match in matches:
            print(f"Job Title: {match['job_title']}, Match Percentage: {match['match_percentage']}%")
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    test_core()