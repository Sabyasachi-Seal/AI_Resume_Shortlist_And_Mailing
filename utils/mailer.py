import re
from email.mime.text import MIMEText
import smtplib
from ollama import Client
from datetime import datetime, timedelta

def extract_email(resume_text):
    """Extract the email address from the resume text."""
    # Simple regex to match common email formats (e.g., "Email: user@example.com")
    email_pattern = r'Email:\s*([\w\.-]+@[\w\.-]+)'
    match = re.search(email_pattern, resume_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    print("Warning: No email found in resume text.")
    return None

def generate_email_with_ollama(resume_file, job_title, match_percentage):
    """Generate a personalized email using an Ollama model."""
    # Placeholder interview time (e.g., 2 days from now at 10:00 AM PDT)
    interview_time = (datetime.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)
    interview_format = "Video call via Zoom"
    
    # Initialize Ollama client
    ollama_client = Client(host='http://localhost:11434')
    
    # Prompt for the model
    prompt = f"""
You are a professional HR assistant. Generate a polite and personalized email invitation for an interview based on the following details:
- Resume File: {resume_file}
- Job Title: {job_title}
- Match Percentage: {match_percentage}%
- Interview Date and Time: {interview_time.strftime('%B %d, %Y, %I:%M %p PDT')}
- Interview Format: {interview_format}
- Company: [Your Company Name]
- Contact Email: contact@yourcompany.com

The email should include:
- A subject line
- A greeting addressing the candidate (e.g., "Dear Candidate")
- A thank you note mentioning the match percentage
- Interview details (date, time, format)
- A call to action for confirmation within 48 hours
- A closing with the company name and contact email

Return the email as a plain text string with each section separated by a newline.
    """
    
    # Invoke the model
    response = ollama_client.chat(model="llama3.2:latest", messages=[{"role": "user", "content": prompt}])
    email_content = response['message']['content'].strip()
    
    # Extract subject (first line) and ensure proper formatting
    lines = email_content.split('\n')
    subject = lines[0].replace("Subject:", "").strip() if lines[0].startswith("Subject:") else f"Interview Invitation for {job_title}"
    body = "\n".join(lines[1:]).strip()
    
    return f"{subject}\n{body}"

def send_email(to_email, email_content):
    """Send the email using SMTP (e.g., Gmail for testing)."""
    # Configure your email credentials (replace with your own)
    from_email = "your_email@gmail.com"
    password = "your_app_password"  # Use an App Password if 2FA is enabled

    # Create MIMEText object
    lines = email_content.split('\n', 1)
    subject = lines[0]
    body = lines[1] if len(lines) > 1 else email_content
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        # Connect to SMTP server (Gmail as an example)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
        print(f"Email successfully sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        print("Email content (for manual sending):")
        print(email_content)