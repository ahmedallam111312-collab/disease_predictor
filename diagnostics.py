from database import db_manager
from config import TEMPERATURE_DIAGNOSIS

class DiagnosticEngine:
    def __init__(self, engine):
        self.engine = engine

    def consult(self, history, confirmed_symptoms, negated_symptoms, language="English"):
        
        # 1. Retrieval
        db_context = db_manager.search_diseases(confirmed_symptoms)
        
        # 2. Dynamic Language Settings
        if language == "Arabic":
            lang_instruction = "Modern Standard Arabic (اللغة العربية الفصحى)"
            forbidden = "English, Korean, Chinese"
        else:
            lang_instruction = "Professional Medical English"
            forbidden = "Arabic, Korean, Chinese"

        # 3. THE UPGRADED "EMERGENCY AWARE" PROMPT
        system_prompt = f"""
        You are a Senior Emergency Physician.
        
        CRITICAL PROTOCOL - READ CAREFULLY:
        1. RED FLAG SCANNING: If the patient has 3+ signs of a LIFE-THREATENING condition (e.g., Chest Pain + Radiation + Exertion), STOP ASKING QUESTIONS. DIAGNOSE IMMEDIATELY.
        2. DO NOT NAGGLE: Do not ask for minor details (like "exact duration") if the big picture is clear (Heart Attack pattern).
        3. SAFETY FIRST: If the condition looks dangerous, your "Management Plan" must start with "CALL EMERGENCY SERVICES" or "GO TO ER".
        
        LANGUAGE RULES:
        - Output 'reply_text', 'diagnosis', 'management' in {lang_instruction}.
        - Do NOT use {forbidden}.

        JSON OUTPUT STRUCTURE:
        {{
            "status": "ask_question" OR "diagnosis_ready",
            "thought_process": "Reasoning in English...",
            "reply_text": "Question/Statement in {language}",
            
            "primary_diagnosis": {{
                "name_user_lang": "Disease Name in {language}",
                "name_english": "English Name",
                "icd_code": "ICD-11 Code",
                "confidence": 0-100,
                "reasoning_user_lang": "Detailed explanation in {language}"
            }},
            "management": {{
                "immediate_user_lang": "URGENT ACTION in {language}",
                "labs": ["Lab Name"]
            }}
        }}
        """
        
        # We explicitly flag the "Red Flags" in the user prompt to wake up the AI
        red_flag_context = ""
        cardiac_triggers = ["chest", "jaw", "arm", "shoulder", "breath", "heart"]
        if any(x in str(confirmed_symptoms).lower() for x in cardiac_triggers):
            red_flag_context = "⚠️ ALERT: SYMPTOMS SUGGEST POSSIBLE CARDIAC EVENT. EVALUATE FOR ACS/MI IMMEDIATELY."

        user_prompt = f"""
        PATIENT HISTORY: {history}
        CONFIRMED SYMPTOMS: {confirmed_symptoms}
        RULED OUT: {negated_symptoms}
        DB CANDIDATES: {db_context}
        {red_flag_context}
        
        Analyze evidence. If >3 strong cardiac/stroke indicators are present, DIAGNOSE NOW.
        """
        
        return self.engine.generate_json(system_prompt, user_prompt, temperature=TEMPERATURE_DIAGNOSIS)

from ai_engine import ai_engine
diagnostics = DiagnosticEngine(ai_engine)