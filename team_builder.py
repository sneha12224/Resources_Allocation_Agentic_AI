# team_builder.py
import streamlit as st
import pandas as pd
from utils import save_json
from core_functions import score_employee

PROJ_FILE = "projects.json"

def render_team_builder():
    st.header("👥 Team Builder")
    
    if not st.session_state.projects:
        st.info("Analyze a project first to build a team")
    else:
        project_options = [f"{i+1}. {p['name']}" for i, p in enumerate(st.session_state.projects)]
        selected_project = st.selectbox("Select Project", options=project_options, index=len(project_options)-1 if project_options else 0)
        project_index = project_options.index(selected_project)
        project = st.session_state.projects[project_index]
        
        st.subheader(f"Team for: {project['name']}")
        st.write(f"**Summary:** {project.get('summary', 'No summary available')}")
        
        # Required skills
        st.write("**Required Skills:**")
        if project.get('required_skills'):
            skills_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0;'>"
            for skill in project['required_skills']:
                skills_html += f"<span style='background-color: #4CAF50; color: white; padding: 5px 12px; border-radius: 15px; font-size: 14px;'>{skill}</span>"
            skills_html += "</div>"
            st.markdown(skills_html, unsafe_allow_html=True)
        
        # Current team
        st.subheader("Current Team")
        if project.get('team'):
            team_data = []
            for emp in project['team']:
                score = score_employee(emp.get("skills", []), project.get('required_skills', []), emp.get("experience", 1))
                team_data.append({
                    "Name": emp['name'],
                    "Skills": ", ".join(emp['skills']),
                    "Experience": f"{emp.get('experience', 1)} years",
                    "Match Score": f"{score}%"
                })
            
            team_df = pd.DataFrame(team_data)
            st.dataframe(team_df, use_container_width=True, hide_index=True)
            
            # Remove buttons
            for i, emp in enumerate(project['team']):
                if st.button(f"Remove {emp['name']}", key=f"remove_{project['id']}_{i}"):
                    project['team'].pop(i)
                    save_json(PROJ_FILE, st.session_state.projects)
                    st.rerun()
        else:
            st.info("No team members selected yet.")
        
        # Available employees
        st.subheader("Available Employees")
        available_emps = [e for e in st.session_state.employees if e not in project.get('team', [])]
        
        if available_emps:
            for i, emp in enumerate(available_emps):
                score = score_employee(emp.get("skills", []), project.get('required_skills', []), emp.get("experience", 1))
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{emp['name']}** - {', '.join(emp['skills'])}")
                with col2:
                    st.write(f"Match: {score}%")
                with col3:
                    if st.button("Add", key=f"add_{i}"):
                        if 'team' not in project:
                            project['team'] = []
                        project['team'].append(emp)
                        save_json(PROJ_FILE, st.session_state.projects)
                        st.rerun()
        else:
            st.info("No available employees.")