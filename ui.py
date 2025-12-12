import streamlit as st
from config import RTL_CSS

# Dictionary for UI Labels
TEXTS = {
    "Arabic": {
        "settings": "⚙️ الإعدادات",
        "api_key": "مفتاح API",
        "patient": "ملف المريض",
        "age": "العمر",
        "history": "التاريخ المرضي",
        "live_memory": "🧠 الذاكرة الطبية",
        "confirmed": "✅ المؤكد:",
        "negated": "❌ المستبعد:",
        "reset": "بدء تشخيص جديد",
        "title": "🏆 التشخيص:",
        "term": "المصطلح الطبي:",
        "conf": "مستوى الثقة:",
        "report": "التقرير الطبي:",
        "labs": "الفحوصات المطلوبة:",
        "plan": "الخطة العلاجية:"
    },
    "English": {
        "settings": "⚙️ Settings",
        "api_key": "Groq API Key",
        "patient": "Patient Profile",
        "age": "Age",
        "history": "Medical History",
        "live_memory": "🧠 Live Logic",
        "confirmed": "✅ Confirmed:",
        "negated": "❌ Ruled Out:",
        "reset": "Start New Consultation",
        "title": "🏆 Diagnosis:",
        "term": "Medical Term:",
        "conf": "Confidence:",
        "report": "Medical Report:",
        "labs": "Required Labs:",
        "plan": "Immediate Plan:"
    }
}

def inject_css(language):
    # Only inject RTL CSS if Arabic is selected
    if language == "Arabic":
        st.markdown(RTL_CSS, unsafe_allow_html=True)
    else:
        # Simple LTR override
        st.markdown("""
        <style>
            .main { direction: ltr; text-align: left; }
            .stTextInput input { direction: ltr; text-align: left; }
            div[data-testid="stChatMessageContent"] { direction: ltr; text-align: left; }
            .report-card { border-right: none; border-left: 6px solid #2e86c1; text-align: left; direction: ltr; }
        </style>
        """, unsafe_allow_html=True)

def render_sidebar(memory, api_key_state):
    with st.sidebar:
        # LANGUAGE SELECTOR
        lang = st.radio("Language / اللغة", ["Arabic", "English"])
        t = TEXTS[lang] # Get localized strings
        
        st.divider()
        st.header(t["settings"])
        
        if not api_key_state:
            key = st.text_input(t["api_key"], type="password")
            if key:
                st.session_state['GROQ_API_KEY'] = key
                st.rerun()
        else:
            st.success("API Key Active")

        st.divider()
        st.header(t["patient"])
        age = st.number_input(t["age"], value=30, step=1)
        history = st.text_area(t["history"], "None")
        
        memory.set_profile(age, history)

        st.divider()
        st.markdown(f"### {t['live_memory']}")
        
        if memory.confirmed:
            st.markdown(f"**{t['confirmed']}**")
            st.code(memory.confirmed)
        
        if memory.negated:
            st.markdown(f"**{t['negated']}**")
            st.code(memory.negated)

        if st.button(t["reset"], type="primary"):
            memory.reset()
            st.rerun()
        
        return lang

def render_chat(messages):
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def render_diagnosis(diagnosis_data, language):
    t = TEXTS[language]
    d = diagnosis_data
    diag = d['primary_diagnosis']
    mgmt = d['management']
    
    st.markdown(f"""
    <div class="report-card">
        <div class="report-header">{t['title']} {diag['name_user_lang']}</div>
        <p><b>{t['term']}</b> {diag['name_english']} (Code: {diag['icd_code']})</p>
        <p><b>{t['conf']}</b> {diag['confidence']}%</p>
        <hr>
        <h4>🧠 {t['report']}</h4>
        <p>{diag['reasoning_user_lang']}</p>
        <h4>🧪 {t['labs']}</h4>
        <div class="lab-list">
            <ul>{''.join(f'<li>{lab}</li>' for lab in mgmt['labs'])}</ul>
        </div>
        <h4>⚡ {t['plan']}</h4>
        <p>{mgmt['immediate_user_lang']}</p>
    </div>
    """, unsafe_allow_html=True)