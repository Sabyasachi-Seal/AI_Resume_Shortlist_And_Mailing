import gradio as gr
from src.processor import ATSVectorProcessor
from utils.helpers import input_pdf_text
from utils.mailer import extract_email, generate_email_with_ollama
import os
import tempfile
import zipfile
from datetime import datetime

# Initialize processor
processor = ATSVectorProcessor(top_n=5)
min_match_percentage = 72.0  # Threshold for shortlisting

def process_resumes(resume_zip='./data/resume/'):

    temp_dir = resume_zip

    resume_files = [f for f in os.listdir(temp_dir) if f.endswith('.pdf')]
    if not resume_files:
        yield "No PDF files found in the uploaded ZIP.", gr.State(value=[]), gr.State(value=[])
        return

    results = []
    shortlisted = []

    for resume_file in resume_files:
        resume_path = os.path.join(temp_dir, resume_file)
        print(f"Processing Resume: {resume_file}")

        # Extract text from the resume
        with open(resume_path, "rb") as f:
            resume_data = f.read()
            temp_path = os.path.join(tempfile.gettempdir(), resume_file)
            with open(temp_path, "wb") as temp_f:
                temp_f.write(resume_data)
            resume_text = input_pdf_text(temp_path)

        # print(f"Resume Text (first 200 chars): {resume_text[:200]}...")

        # Extract email from resume
        candidate_email = extract_email(resume_text)

        # Analyze the resume
        try:
            matches = processor.analyze(resume_text)
            best_match = matches[0] if matches and "match_percentage" in matches[0] else {"job_title": "N/A", "match_percentage": 0.0}

            # Determine shortlist status and generate email if applicable
            is_shortlisted = best_match["match_percentage"] >= min_match_percentage and candidate_email
            email_content = generate_email_with_ollama(resume_file, best_match["job_title"], best_match["match_percentage"]) if is_shortlisted else None

            # Convert to list for Dataframe
            current_result = [
                resume_file,
                best_match["job_title"],
                f"{best_match['match_percentage']}%",
                "Yes" if is_shortlisted else "No",
                email_content if email_content else "N/A"
            ]
            results.append(current_result)

            if is_shortlisted:
                shortlisted.append([
                    resume_file,
                    best_match["job_title"],
                    best_match["match_percentage"],
                    email_content if email_content else "N/A"
                ])

            # Yield live update
            yield (
                f"Processing {resume_file}...",
                results,
                shortlisted
            )

        except Exception as e:
            print(f"Error processing {resume_file}: {str(e)}")
            current_result = [resume_file, "Error", "N/A", "No", "N/A"]
            results.append(current_result)
            yield (
                f"Error processing {resume_file}: {str(e)}",
                results,
                shortlisted
            )

    # Final yield with completion status
    yield (
        "Resumes processed successfully.",
        results,
        shortlisted
    )

# Gradio interface
with gr.Blocks(title="Smart ATS with Ollama") as demo:
    gr.Markdown("""
    # Smart ATS Using Ollama
    Process resume PDFs in real-time to identify the best-matched job, determine shortlisting eligibility, and generate personalized emails for shortlisted candidates.
    """)

    
    with gr.Row():
        status_output = gr.Textbox(label="Status", lines=1)
        results_output = gr.Dataframe(label="Processing Results", headers=["Resume", "Most Matched Job", "Match Percentage", "Shortlisted", "Email"])
        shortlisted_output = gr.Dataframe(label="Shortlisted Candidates", headers=["Resume", "Most Matched Job", "Match Percentage", "Email"])

    submit_btn = gr.Button("Process Resumes")
    submit_btn.click(
        fn=process_resumes,
        outputs=[status_output, results_output, shortlisted_output],
        api_name="process"
    )

demo.launch(inbrowser=True, show_error=True, debug=True)