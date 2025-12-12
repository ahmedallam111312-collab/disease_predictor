from ai_engine import ai_engine

class SymptomExtractor:
    def __init__(self, engine):
        self.engine = engine

    def process_input(self, user_text, current_confirmed, last_question):
        """
        Analyzes Arabic input.
        Returns: Dict with added symptoms, removed symptoms, and negations (ALL IN ENGLISH).
        """
        system_prompt = f"""
        You are a Semantic Medical Interpreter.
        
        CONTEXT:
        - Confirmed Symptoms: {current_confirmed}
        - Doctor's Last Question: "{last_question}"
        - Patient Answer: "{user_text}" (Likely Arabic)
        
        TASK:
        1. Interpret the Patient's Answer based on the Doctor's Question.
        2. Translate concepts to STANDARD ENGLISH MEDICAL TERMS (SNOMED-CT style).
        3. DEDUPLICATE: If a symptom implies the same concept as one in the list (e.g. "Painful breathing" vs "Dyspnea"), DO NOT add it.
        4. DETECT NEGATION: If user says "No" to a specific symptom, add to 'negated'.
        5. DETECT CORRECTION: If user denies something previously confirmed, add to 'remove'.

        OUTPUT JSON:
        {{
            "new_symptoms_english": ["Term1", "Term2"],
            "negated_symptoms_english": ["Term3"],
            "remove_symptoms": ["Term4"]
        }}
        """

        # Provide a dummy user prompt as context is embedded in system prompt
        response = self.engine.generate_json(system_prompt, "Extract symptoms", temperature=0.0)
        
        if response.get("status") == "error":
            return {"new_symptoms_english": [], "negated_symptoms_english": [], "remove_symptoms": []}
        
        return response

extractor = SymptomExtractor(ai_engine)