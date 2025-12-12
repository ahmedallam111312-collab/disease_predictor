import streamlit as st
import os
from config import GROQ_API_KEY
from memory import PatientMemory
from ai_engine import ai_engine
from extractor import extractor
from diagnostics import diagnostics
from ui import inject_css, render_sidebar, render_chat, render_diagnosis

# 1. Setup
st.set_page_config(page_title="Tabib AI Pro", page_icon="🩺", layout="wide")

# 2. Initialize Memory
memory = PatientMemory()

# 3. API Key
api_key = st.session_state.get('GROQ_API_KEY', GROQ_API_KEY)
if api_key:
    ai_engine.client.api_key = api_key 

# 4. Sidebar & Language Selection
# render_sidebar now returns the selected language
selected_language = render_sidebar(memory, api_key)

# 5. Inject CSS based on language (RTL vs LTR)
inject_css(selected_language)

# 6. Main Title
title = "🩺 طبيب الذكاء الاصطناعي" if selected_language == "Arabic" else "🩺 AI Medical Specialist"
st.title(title)

# 7. Render Chat
render_chat(memory.messages)

# 8. Main Logic
if st.session_state.get('diagnosis'):
    render_diagnosis(st.session_state.diagnosis, selected_language)
    
    lbl = "بدء تشخيص جديد" if selected_language == "Arabic" else "Start New Consultation"
    if st.button(lbl, key="reset_bottom"):
        memory.reset()
        st.rerun()

elif prompt := st.chat_input("..."):
    
    if not api_key:
        st.error("API Key Missing / مفتاح API مفقود")
        st.stop()

    memory.add_message("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Extraction (The extractor works in English internally, so it supports both languages naturally)
    with st.status("..." if selected_language == "English" else "جاري التحليل...", expanded=False) as status:
        extraction_data = extractor.process_input(
            prompt, 
            memory.confirmed, 
            memory.last_question
        )
        memory.update_symptoms(
            extraction_data.get('new_symptoms_english', []),
            extraction_data.get('negated_symptoms_english', []),
            extraction_data.get('remove_symptoms', [])
        )
        status.update(label="Complete", state="complete", expanded=False)

    # Reasoning (Pass the selected language!)
    with st.spinner("..." if selected_language == "English" else "جاري استشارة الطبيب..."):
        decision = diagnostics.consult(
            memory.get_history_str(),
            memory.confirmed,
            memory.negated,
            language=selected_language # <--- NEW PARAMETER
        )

    if decision.get("status") == "error":
        st.error(f"Error: {decision.get('error')}")
    
    elif decision.get("status") == "ask_question":
        # Note: key is now 'reply_text' to match the new generic prompt
        question = decision['reply_text'] 
        memory.last_question = question
        memory.add_message("assistant", question)
        
        with st.chat_message("assistant"):
            st.markdown(question)
            
    elif decision.get("status") == "diagnosis_ready":
        st.session_state.diagnosis = decision
        st.rerun()