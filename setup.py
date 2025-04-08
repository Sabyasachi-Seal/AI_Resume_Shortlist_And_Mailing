from setuptools import setup, find_packages

setup(
    name="AI_Shortlist",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "gradio",
        "PyPDF2",
        "langchain-community",
        "ollama",
        "sqlite3",
        "yacana"  
    ],
    author="Sabyasachi Seal",
    description="AI Shortlist: A tool for shortlisting candidate resumes using AI",
)