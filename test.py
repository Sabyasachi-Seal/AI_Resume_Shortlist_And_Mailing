import os
from src.processor import ATSVectorProcessor
import tempfile
from utils.mailer import extract_email, generate_email, send_email
from utils.helpers import input_pdf_text

def test_core():
    # Process all resumes from /data/resumes/
    resumes_dir = "./data/resume/"
    if not os.path.exists(resumes_dir):
        print(f"Error: {resumes_dir} not found. Please add resume PDFs to this directory.")
        return

    resume_files = [f for f in os.listdir(resumes_dir) if f.endswith('.pdf')]
    if not resume_files:
        print(f"Error: No PDF files found in {resumes_dir}.")
        return

    processor = ATSVectorProcessor(top_n=5)
    min_match_percentage = 72.0  # Threshold for selection
    selected_resumes = []

    for resume_file in resume_files:
        sample_resume_file = os.path.join(resumes_dir, resume_file)
        print(f"\nProcessing Resume: {resume_file}")

        # Extract text from the resume
        with open(sample_resume_file, "rb") as f:
            resume_data = f.read()
            resume_path = os.path.join(tempfile.gettempdir(), resume_file)
            with open(resume_path, "wb") as temp_f:
                temp_f.write(resume_data)
            resume_text = input_pdf_text(resume_path)

        print(f"Resume Text (first 200 chars): {resume_text[:200]}...")

        # Extract email from resume
        candidate_email = extract_email(resume_text)

        # Analyze the resume
        try:
            matches = processor.analyze(resume_text)
            best_match = matches[0] if matches and "match_percentage" in matches[0] else {"job_title": "N/A", "match_percentage": 0.0}
            print(f"Best Match: Job Title: {best_match['job_title']}, Match Percentage: {best_match['match_percentage']}%")
            print(f"Extracted Email: {candidate_email}")

            # Select if match percentage is above threshold and send email
            if best_match["match_percentage"] >= min_match_percentage and candidate_email:
                selected_resumes.append({
                    "resume_file": resume_file,
                    "best_job_title": best_match["job_title"],
                    "match_percentage": best_match["match_percentage"],
                    "email": candidate_email
                })
                email_content = generate_email(resume_file, best_match["job_title"], best_match["match_percentage"])
                print(f"Generated Email Content:\n{email_content}")
                # send_email(candidate_email, email_content)
        except Exception as e:
            print(f"Error processing {resume_file}: {str(e)}")

    # Output selected resumes summary
    if selected_resumes:
        print("\nSelected Resumes (above 60% match):")
        for resume in selected_resumes:
            print(f"Resume: {resume['resume_file']}, Best Job Title: {resume['best_job_title']}, Match Percentage: {resume['match_percentage']}%, Email: {resume['email']}")
    else:
        print("\nNo resumes selected (none above 60% match or missing email).")

if __name__ == "__main__":
    test_core()