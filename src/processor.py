from langchain_ollama import OllamaLLM  # Updated import
from utils.helpers import get_embeddings, cosine_similarity, save_to_sqlite
import json
import numpy as np

class ATSProcessor:
    def __init__(self, max_retries=3):
        try:
            self.model = OllamaLLM(base_url='http://localhost:11434', model='ats_model')
            self.max_retries = max_retries  # Maximum number of feedback attempts
        except Exception as e:
            raise Exception(f"Error initializing Ollama model: {e}")

    def analyze(self, job_desc, resume_text):
        """Analyze JD and resume with a feedback loop for JSON errors, handling code blocks."""
        attempt = 0
        prompt = f"Job Description-{job_desc} Resume-{resume_text}"
        response = None

        while attempt < self.max_retries:
            try:
                # Initial or feedback invocation
                response = self.model.invoke(prompt if attempt == 0 else self._build_feedback_prompt(prompt, response, "Previous response was not valid JSON"))
                
                # Remove ``` code block markers if present
                if response.strip().startswith("```") and response.strip().endswith("```"):
                    response = response.strip().replace("```json\n", "").replace("\n```", "").strip()
                    print(f"Removed code block markers. Adjusted response: {response[:200]}...")

                # Attempt to parse JSON
                result = json.loads(response)

                # Generate embeddings and calculate score
                embeddings = get_embeddings([job_desc, resume_text])
                jd_embedding = np.array(embeddings[0])
                resume_embedding = np.array(embeddings[1])
                score = cosine_similarity(jd_embedding, resume_embedding)
                result["score"] = int(score)

                # Save to SQLite
                save_to_sqlite(job_desc, resume_text, json.dumps(result))

                return result
            except json.JSONDecodeError as e:
                print(f"Attempt {attempt + 1} failed: {e}. Raw response: {response}")
                attempt += 1
                if attempt == self.max_retries:
                    return {"error": f"Failed to parse JSON after {self.max_retries} attempts. Raw response: {response}"}
                # Build feedback prompt, noting code block issue if applicable
                feedback_error = f"Previous response contained invalid JSON{', including code block markers ```' if '```' in response else ''}. Error: {str(e)}"
                prompt = self._build_feedback_prompt(prompt, response, feedback_error)
            except Exception as e:
                return {"error": str(e)}

    def _build_feedback_prompt(self, original_prompt, previous_response, error):
        """Construct a feedback prompt with input, output, and error."""
        feedback = f"""
        Original Prompt: {original_prompt}
        Previous Response: {previous_response}
        Error: {error}
        Please correct the response and return it as a valid JSON object with the structure:
        {{
          "jd_keywords": [],
          "resume_keywords": [],
          "mismatches": []
        }}
        Ensure the output is strictly raw JSON, without ``` code block markers, even if data is incomplete. Use empty arrays ([]) if no keywords or mismatches are found.
        """
        return feedback