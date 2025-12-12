import sqlite3
import streamlit as st
from config import DB_NAME

class DatabaseManager:
    def __init__(self, db_path=DB_NAME):
        self.db_path = db_path

    def _get_connection(self):
        """Creates a thread-safe connection."""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    @st.cache_data(ttl=3600, show_spinner=False)
    def search_diseases(_self, symptoms: list[str]) -> str:
        """
        Optimized search: Finds diseases matching the most symptoms.
        Uses caching to prevent hitting DB on every interaction.
        """
        if not symptoms:
            return "No symptoms provided."

        # Search logic: Prioritize specific matches
        # We look at the last 4 symptoms for relevance context
        active_symptoms = symptoms[-4:]
        
        # Safe parameterized query construction
        placeholders = ','.join('?' for _ in active_symptoms)
        
        # Scoring Query: Rank diseases by how many symptoms match
        query = f"""
        SELECT d.code, d.title, d.definition, COUNT(df.feature_id) as match_count
        FROM diseases d
        JOIN disease_features df ON d.code = df.disease_code
        JOIN features f ON df.feature_id = f.id
        WHERE f.name IN ({placeholders})
        GROUP BY d.code
        ORDER BY match_count DESC
        LIMIT 8
        """

        conn = _self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, active_symptoms)
            results = cursor.fetchall()
            
            if not results:
                return "No exact database matches found. Relying on General Medical Knowledge."

            formatted_results = ""
            for code, title, definition, count in results:
                # Truncate definition for token efficiency
                short_def = (definition[:150] + '...') if definition else "No definition."
                formatted_results += f"- [ICD-11: {code}] {title} (Matches: {count}): {short_def}\n"
            
            return formatted_results

        except sqlite3.Error as e:
            return f"Database Error: {e}"
        finally:
            conn.close()

# Singleton Instance
db_manager = DatabaseManager()