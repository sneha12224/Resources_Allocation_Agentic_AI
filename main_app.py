# main_app.py
import streamlit as st
import os
from dotenv import load_dotenv
from project_analysis import render_project_analysis
from team_builder import render_team_builder
from employee_database import render_employee_database
from analytics import render_analytics
from ai_advisor import render_ai_advisor
from utils import load_json_if_exists, save_json, initialize_session_state

# Load env variables
load_dotenv()

# File names
EMP_FILE = "employees.json"
PROJ_FILE = "projects.json"
CHAT_FILE = "chat_history.json"
KNOWLEDGE_FILE = "knowledge_base.json"

# ------------- Page setup ----------------
st.set_page_config(page_title="Resource Allocation Agent", page_icon="🤖", layout="wide")
st.title("🤖 Advanced Resource Allocation Agent")
st.caption("Intelligent Employee → Project Assignment System with AI-Powered Insights")

# Initialize session state
initialize_session_state(EMP_FILE, PROJ_FILE, CHAT_FILE, KNOWLEDGE_FILE)

# ------------------ Sidebar ------------------
def render_sidebar():
    st.sidebar.header("Settings")
    st.sidebar.write("Mode: " + os.getenv("MODE", "gemini"))

    # Debug section
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### Debug Info")
    if os.getenv("GEMINI_API_KEY"):
        st.sidebar.success("API Key: Configured")
    else:
        st.sidebar.error("API Key: Missing")
    st.sidebar.info(f"Mode: {os.getenv('MODE', 'gemini')}")

    st.sidebar.markdown("#### Employee Management")
    if st.sidebar.button("Load Default Employees"):
        default_employees = [
            {"name": "Alice", "skills": ["Python", "AI/ML", "SQL"], "experience": 3, "workload": 0},
            {"name": "Bob", "skills": ["React", "Design", "Figma"], "experience": 2, "workload": 0},
            {"name": "Charlie", "skills": ["Django", "Flask", "DevOps"], "experience": 4, "workload": 0},
            {"name": "David", "skills": ["AWS", "Docker", "Kubernetes"], "experience": 5, "workload": 0},
            {"name": "Eva", "skills": ["C++", "Embedded", "Testing"], "experience": 2, "workload": 0},
            {"name": "Frank", "skills": ["Node", "React", "MongoDB"], "experience": 3, "workload": 0},
            {"name": "Grace", "skills": ["Data Science", "Python", "SQL"], "experience": 4, "workload": 0}
        ]
        st.session_state.employees = default_employees
        save_json(EMP_FILE, st.session_state.employees)
        st.sidebar.success("Loaded default employees")

    st.sidebar.markdown("#### Add New Employee")
    with st.sidebar.form("add_employee_form"):
        name = st.text_input("Name")
        skills = st.multiselect("Skills", ["Python", "AI/ML", "React", "JavaScript", "Database", 
                                          "DevOps", "Blockchain", "Security", "Cloud", "Design", "Go", "Golang"])
        experience = st.slider("Experience (years)", 1, 10, 2)
        submitted = st.form_submit_button("Add Employee")
        if submitted and name:
            st.session_state.employees.append({"name": name, "skills": skills, "experience": experience, "workload": 0})
            save_json(EMP_FILE, st.session_state.employees)
            st.sidebar.success(f"Added {name}")

# Render sidebar
render_sidebar()

# ------------------ Main Interface (tabs) ------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Project Analysis", "Team Builder", "Employee Database", "Analytics", "AI Advisor"])

with tab1:
    render_project_analysis()

with tab2:
    render_team_builder()

with tab3:
    render_employee_database()

with tab4:
    render_analytics()

with tab5:
    render_ai_advisor()