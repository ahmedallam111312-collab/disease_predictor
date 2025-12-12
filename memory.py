import streamlit as st

class PatientMemory:
    """Encapsulates Streamlit Session State for the patient."""
    
    def __init__(self):
        self._init_state()

    def _init_state(self):
        defaults = {
            "messages": [],
            "confirmed_symptoms": [], # English standardized
            "negated_symptoms": [],   # English standardized
            "last_question": "None",
            "diagnosis": None,
            "patient_profile": {}
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

    @property
    def confirmed(self):
        return st.session_state.confirmed_symptoms

    @property
    def negated(self):
        return st.session_state.negated_symptoms

    @property
    def messages(self):
        return st.session_state.messages

    @property
    def last_question(self):
        return st.session_state.last_question
    
    @last_question.setter
    def last_question(self, value):
        st.session_state.last_question = value

    def add_message(self, role, content):
        st.session_state.messages.append({"role": role, "content": content})

    def update_symptoms(self, new_confirmed, new_negated, to_remove):
        """Smart update: Add new, remove duplicates/contradictions."""
        
        # 1. Handle Removals (Corrections)
        for item in to_remove:
            if item in self.confirmed:
                self.confirmed.remove(item)
        
        # 2. Add Confirmed (Deduplication)
        for item in new_confirmed:
            if item not in self.confirmed and item not in self.negated:
                self.confirmed.append(item)
        
        # 3. Add Negated
        for item in new_negated:
            if item not in self.negated:
                self.negated.append(item)
                # If it was previously confirmed, remove it (correction)
                if item in self.confirmed:
                    self.confirmed.remove(item)

    def set_profile(self, age, history):
        st.session_state.patient_profile = {"age": age, "history": history}

    def get_history_str(self):
        p = st.session_state.patient_profile
        return f"Age: {p.get('age', 'N/A')}, History: {p.get('history', 'None')}"

    def reset(self):
        st.session_state.clear()
        self._init_state()

# REMOVED: memory = PatientMemory() 
# We will instantiate this in app.py instead