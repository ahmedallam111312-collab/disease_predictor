import json
import time
from groq import Groq
from config import MODEL_NAME, GROQ_API_KEY

class AIEngine:
    def __init__(self, api_key=None):
        self.client = None
        key_to_use = api_key or GROQ_API_KEY
        if key_to_use:
            self.client = Groq(api_key=key_to_use)

    def generate_json(self, system_prompt: str, user_prompt: str, temperature: float = 0.1, retries=3) -> dict:
        """
        Executes an AI call enforcing JSON output. 
        Includes exponential backoff for API stability.
        """
        if not self.client:
            return {"status": "error", "error": "Missing API Key"}

        for attempt in range(retries):
            try:
                completion = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    model=MODEL_NAME,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                
                content = completion.choices[0].message.content
                return json.loads(content)

            except json.JSONDecodeError:
                continue # Retry if JSON is malformed
            except Exception as e:
                if attempt == retries - 1:
                    return {"status": "error", "error": str(e)}
                time.sleep(1 * (attempt + 1)) # Backoff

        return {"status": "error", "error": "Max retries exceeded"}

# Singleton Instance placeholder (initialized in app.py)
ai_engine = AIEngine()