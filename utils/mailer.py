import re
from email.mime.text import MIMEText
import smtplib
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

def generate_email(resume_file, job_title, match_percentage):
    """Generate a personalized email for the candidate."""
    # Placeholder interview time (e.g., 2 days from now at 10:00 AM PDT)
    interview_time = (datetime.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)
    interview_format = "Video call via Zoom"
    
    email_content = f"""
Subject: Interview Invitation for {job_title} Position

Dear Candidate (Resume: {resume_file}),

Thank you for applying! Based on your impressive match (score: {match_percentage}%), we are pleased to invite you for an interview for the {job_title} position.

Interview Details:
- Date and Time: {interview_time.strftime('%B %d, %Y, %I:%M %p PDT')}
- Format: {interview_format}
- Next Steps: Please confirm your availability by replying to this email within 48 hours. A Zoom link will be sent upon confirmation.

We look forward to discussing your qualifications further!

Best regards,
The Hiring Team
[Your Company Name]
contact@yourcompany.com
    """
    return email_content.strip()

def send_email(to_email, email_content):
    """Send the email using SMTP (e.g., Gmail for testing)."""
    # Configure your email credentials (replace with your own)
    from_email = "your_email@gmail.com"
    password = "your_app_password"  # Use an App Password if 2FA is enabled

    # Create MIMEText object
    msg = MIMEText(email_content)
    msg['Subject'] = email_content.split('\n')[0][8:]  # Extract subject from content
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