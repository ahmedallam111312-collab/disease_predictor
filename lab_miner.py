import sqlite3
import re

DB_NAME = "icd11_data.db"

# 1. EXPANDED LAB DICTIONARY
# Maps raw text keywords to (Standard Test Name, Category)
LAB_KEYWORDS = {
    # Blood Count
    "leukocyt": ("CBC (White Blood Cells)", "Blood"),
    "white blood cell": ("CBC (White Blood Cells)", "Blood"),
    "neutrophil": ("CBC (Neutrophils)", "Blood"),
    "eosinophil": ("CBC (Eosinophils)", "Blood"),
    "platelet": ("CBC (Platelets)", "Blood"),
    "thrombocyt": ("CBC (Platelets)", "Blood"),
    "hemoglobin": ("CBC (Hemoglobin)", "Blood"),
    "anaemia": ("CBC (Hemoglobin)", "Blood"),
    "anemia": ("CBC (Hemoglobin)", "Blood"),
    
    # Inflammation
    "crp": ("C-Reactive Protein", "Inflammation"),
    "esr": ("Erythrocyte Sedimentation Rate", "Inflammation"),
    "sedimentation rate": ("Erythrocyte Sedimentation Rate", "Inflammation"),

    # Organ Function
    "creatinine": ("Kidney Function Test", "Kidney"),
    "urea": ("Kidney Function Test", "Kidney"),
    "liver enzyme": ("Liver Function Test", "Liver"),
    "transaminase": ("Liver Function Test", "Liver"),
    "alt": ("Liver Function Test", "Liver"),
    "ast": ("Liver Function Test", "Liver"),
    "bilirubin": ("Liver Function Test", "Liver"),

    # Microbiology
    "culture": ("Microbial Culture", "Microbiology"),
    "gram stain": ("Gram Stain", "Microbiology"),
    "pcr": ("PCR Analysis", "Genetics"),
    
    # Imaging/Biopsy
    "biopsy": ("Biopsy", "Pathology"),
    "histolog": ("Histopathology", "Pathology"),
    "x-ray": ("X-Ray", "Imaging"),
    "ct scan": ("CT Scan", "Imaging"),
    "mri": ("MRI", "Imaging"),
    "ultrasound": ("Ultrasound", "Imaging")
}

# 2. DIRECTION PATTERNS (The Logic for High/Low)
DIRECTIONS = {
    "HIGH": ["elevated", "increased", "high", "rise in", "excess", "leukocytosis", "neutrophilia"],
    "LOW": ["decreased", "low", "reduced", "deficiency", "lack of", "thrombocytopenia", "leukopenia", "anemia"],
    "POSITIVE": ["positive", "presence of", "detected", "found", "isolation of", "demonstration of"],
    "ABNORMAL": ["abnormal", "irregular", "dysfunction", "altered"]
}

def get_db_connection():
    return sqlite3.connect(DB_NAME, timeout=10)

def analyze_lab_context(text, keyword):
    """
    Looks at the text AROUND the keyword to decide if it is High, Low, or Positive.
    Returns: (Specific Finding String, Direction Category)
    """
    # Create a snippet window (e.g., 5 words before and 5 words after)
    # This regex grabs the keyword and surrounding context
    pattern = r"(\w+\s+){0,5}" + re.escape(keyword) + r"(\s+\w+){0,5}"
    match = re.search(pattern, text, re.IGNORECASE)
    
    if not match:
        return (f"Check {keyword}", "CHECK")

    snippet = match.group(0).lower()
    found_direction = "CHECK" # Default if we can't tell

    # Check for directional words in the snippet
    for direction_cat, indicators in DIRECTIONS.items():
        for indicator in indicators:
            if indicator in snippet:
                found_direction = direction_cat
                break
        if found_direction != "CHECK":
            break
            
    # Clean up the snippet for display
    clean_finding = snippet.replace("\n", " ").strip()
    return (clean_finding, found_direction)

def run_lab_mining():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("📖 Reading disease definitions...")
    cursor.execute("SELECT code, title, definition FROM diseases WHERE definition IS NOT NULL")
    diseases = cursor.fetchall()
    
    count_linked = 0
    
    print(f"🔍 Deep Scanning {len(diseases)} diseases for Lab Results...")

    for code, title, definition in diseases:
        text_lower = definition.lower()
        
        for keyword, (std_name, category) in LAB_KEYWORDS.items():
            if keyword in text_lower:
                # 1. Determine High/Low/Positive
                finding_text, direction = analyze_lab_context(definition, keyword)
                
                # 2. Insert Lab Name
                cursor.execute("INSERT OR IGNORE INTO lab_tests (name) VALUES (?)", (std_name,))
                cursor.execute("SELECT id FROM lab_tests WHERE name = ?", (std_name,))
                lab_id = cursor.fetchone()[0]
                
                # 3. Insert Detailed Finding
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO disease_labs (disease_code, lab_id, finding, direction)
                        VALUES (?, ?, ?, ?)
                    ''', (code, lab_id, finding_text, direction))
                    count_linked += 1
                except sqlite3.Error:
                    pass

    conn.commit()
    conn.close()
    print(f"✅ Finished. Mined {count_linked} detailed lab results.")

if __name__ == "__main__":
    run_lab_mining()