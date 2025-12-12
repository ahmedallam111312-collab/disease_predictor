import os

# ================= CREDENTIALS =================
# 🔑 PASTE YOUR KEY INSIDE THE QUOTES BELOW
# Example: "gsk_xYz123..."
HARDCODED_KEY = "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"

# Logic: Use the hardcoded key if it exists, otherwise check Environment variables
GROQ_API_KEY = HARDCODED_KEY if HARDCODED_KEY.startswith("gsk_") else os.environ.get("GROQ_API_KEY")

# ================= CONSTANTS =================
DB_NAME = "icd11_data.db"
MODEL_NAME = "llama-3.3-70b-versatile"
MAX_HISTORY_CONTEXT = 10
TEMPERATURE_DIAGNOSIS = 0.1
TEMPERATURE_CHAT = 0.3

# ================= UI STYLES =================
RTL_CSS = """
<style>
    .main { direction: rtl; text-align: right; }
    .stTextInput input { direction: rtl; text-align: right; }
    div[data-testid="stChatMessageContent"] { direction: rtl; text-align: right; }
    
    .report-card {
        background-color: #f8f9fa;
        padding: 25px;
        border-radius: 12px;
        border-right: 6px solid #2e86c1;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 20px;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
"""
