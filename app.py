import gradio as gr
from src.processor import analyze_jd_resume
from utils.helpers import input_pdf_text
import pandas as pd
import os
import json
import tempfile

# Load JDs from CSV
jds_df = pd.read_csv("./data/jds.csv", encoding="ISO-8859-1")
job_options = jds_df['Job Title'].tolist()

def process_input(job_title: str, resume_file):
    if not job_title or not resume_file:
        return "Please select a job title and upload a resume.", None, None
    
    print(f"Job Title: {job_title}")
    print(f"Resume File: {resume_file.name}")

    try:

        # Get job description from CSV
        job_desc = jds_df[jds_df['Job Title'] == job_title]['Job Description'].iloc[0]
        

        # Extract text from uploaded resume
        resume_path = os.path.join(tempfile.gettempdir(), resume_file.name)
        with open(resume_path, "wb") as f:
            f.write(resume_file.getbuffer())
        resume_text = input_pdf_text(resume_path)

        # Analyze
        result = analyze_jd_resume(job_desc, resume_text)

        return json.dumps(result, indent=2), str(result.get("score", "N/A")), None
    except Exception as e:
        return f"Error: {str(e)}", None, None

# Gradio interface
with gr.Blocks(title="Smart ATS with Gradio") as demo:
    gr.Markdown("""
    # Smart ATS Using Ollama
    Analyze job descriptions and resumes with a custom Ollama model. Select a job title and upload a resume to get a matching analysis.
    """)
    
    with gr.Row():
        job_dropdown = gr.Dropdown(choices=job_options, label="Select Job Title")
        resume_upload = gr.File(label="Upload Resume")
    
    with gr.Row():
        result_output = gr.Textbox(label="Analysis Result (JSON)", lines=10)
        score_output = gr.Textbox(label="Matching Score", lines=1)
        error_output = gr.Textbox(label="Error (if any)", lines=2)

    submit_btn = gr.Button("Analyze")
    submit_btn.click(
        fn=process_input,
        inputs={job_dropdown, resume_upload},
        outputs=[result_output, score_output, error_output],
    )

demo.launch(inbrowser=True, show_error=True, debug=True)