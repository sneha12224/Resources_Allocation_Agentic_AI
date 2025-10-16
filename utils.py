# utils.py
import json
import os
import streamlit as st

# Helpful save/load functions
def load_json_if_exists(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Could not save {path}: {e}")

def initialize_session_state(EMP_FILE, PROJ_FILE, CHAT_FILE, KNOWLEDGE_FILE):
    """Initialize session state variables"""
    if 'employees' not in st.session_state:
        st.session_state.employees = load_json_if_exists(EMP_FILE, [])
    if 'projects' not in st.session_state:
        st.session_state.projects = load_json_if_exists(PROJ_FILE, [])
    if 'selected_employees' not in st.session_state:
        st.session_state.selected_employees = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = load_json_if_exists(CHAT_FILE, [])
    if 'knowledge_base' not in st.session_state:
        from knowledge_base import ADVANCED_KNOWLEDGE
        st.session_state.knowledge_base = load_json_if_exists(KNOWLEDGE_FILE, ADVANCED_KNOWLEDGE)
    if 'ai_predictions' not in st.session_state:
        st.session_state.ai_predictions = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""