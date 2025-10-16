# project_analysis.py
import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
from utils import save_json
from ai_functions import predict_project_parameters, predict_project_summary, predict_required_skills
from core_functions import build_optimal_team, analyze_skill_gaps, calculate_project_timeline, estimate_project_cost

PROJ_FILE = "projects.json"

def render_project_analysis():
    st.header("📥 Enter Project Details")
    
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Project Name", placeholder="e.g., AI-Powered Healthcare Diagnostic System")
        project_desc = st.text_area("Project Description:", height=150, 
                                  placeholder="Describe your project in detail...")
        
        if st.button("🤖 AI Predict Parameters"):
            if project_desc.strip():
                with st.spinner("AI predicting project parameters..."):
                    predictions = predict_project_parameters(project_desc)
                    st.session_state.ai_predictions = predictions
                    st.success("Parameters predicted! Review and adjust below.")
            else:
                st.warning("Please enter project description first")
    
    with col2:
        if st.session_state.ai_predictions:
            predictions = st.session_state.ai_predictions
            st.write("### AI Predictions")
            st.info(f"**Summary:** {predictions.get('summary', 'No summary available')}")
            
            col2a, col2b = st.columns(2)
            with col2a:
                project_complexity = st.select_slider("Project Complexity", 
                                                    options=["low", "medium", "high", "very high"],
                                                    value=predictions["complexity"])
                team_size = st.slider("Team Size", 1, 10, predictions["recommended_team_size"])
                st.write(f"**AI Recommended:** {predictions['recommended_team_size']} people")
                
            with col2b:
                budget = st.number_input("Budget ($)", min_value=1000, 
                                       value=predictions["estimated_budget"], step=1000)
                st.info(f"**Timeline:** {predictions['timeline_weeks']} weeks")
                st.info(f"**Risk Level:** {predictions['risk_level']}")
                
            # Show key technologies
            if predictions.get("key_technologies"):
                st.write("**Key Technologies:**")
                tech_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0;'>"
                for tech in predictions["key_technologies"]:
                    tech_html += f"<span style='background-color: #FF6B6B; color: white; padding: 5px 12px; border-radius: 15px; font-size: 14px;'>{tech}</span>"
                tech_html += "</div>"
                st.markdown(tech_html, unsafe_allow_html=True)
        else:
            project_complexity = st.select_slider("Project Complexity", 
                                                options=["low", "medium", "high", "very high"])
            team_size = st.slider("Team Size", 1, 10, 3)
            budget = st.number_input("Budget ($)", min_value=1000, value=10000, step=1000)

    if st.button("🚀 Analyze Project & Build Team", type="primary"):
        if not project_desc.strip():
            st.warning("Please enter a project description first.")
        else:
            with st.spinner("AI analyzing project and building team..."):
                # Get summary from AI predictions or generate one
                if st.session_state.ai_predictions:
                    summary = st.session_state.ai_predictions.get("summary", predict_project_summary(project_desc))
                else:
                    summary = predict_project_summary(project_desc)
                
                # Predict required skills
                required_skills = predict_required_skills(project_desc)
                
                # Build optimal team
                selected_team, all_scored_employees = build_optimal_team(required_skills, st.session_state.employees, team_size)
                
                # Analyze skill gaps
                skill_gaps = analyze_skill_gaps(required_skills, st.session_state.employees)
                
                # Calculate project metrics
                timeline = calculate_project_timeline(project_complexity, len(selected_team))
                estimated_cost = estimate_project_cost(selected_team, timeline)
                
                # Store project data
                project_data = {
                    "id": str(uuid.uuid4()),
                    "name": project_name or f"Project {len(st.session_state.projects) + 1}",
                    "description": project_desc,
                    "summary": summary,
                    "required_skills": required_skills,
                    "complexity": project_complexity,
                    "team_size": team_size,
                    "timeline": timeline,
                    "estimated_cost": estimated_cost,
                    "budget": budget,
                    "team": selected_team,
                    "skill_gaps": skill_gaps,
                    "all_scored_employees": all_scored_employees,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.projects.append(project_data)
                st.session_state.selected_employees = selected_team
                save_json(PROJ_FILE, st.session_state.projects)
            
            # Display results
            st.subheader("📊 Project Analysis Results")
            
            # Project Summary
            st.subheader("📌 Project Summary")
            st.info(summary)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Team Size", len(selected_team))
            with col2:
                st.metric("Timeline (days)", timeline)
            with col3:
                st.metric("Estimated Cost", f"${estimated_cost:,.0f}")
            
            # Required Skills
            st.subheader("✅ Predicted Required Skills")
            if required_skills:
                skills_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0;'>"
                for skill in required_skills:
                    skills_html += f"<span style='background-color: #4CAF50; color: white; padding: 5px 12px; border-radius: 15px; font-size: 14px;'>{skill}</span>"
                skills_html += "</div>"
                st.markdown(skills_html, unsafe_allow_html=True)
                
                # Skill Gap Analysis
                if skill_gaps["missing_skills"]:
                    st.subheader("⚠ Skill Gaps Identified")
                    st.warning(f"Missing skills: {', '.join(skill_gaps['missing_skills'])}")
                    st.info(f"Skill coverage: {skill_gaps['coverage_percentage']}%")
                else:
                    st.success("✅ All required skills are available in your team!")
            else:
                st.info("No specific skills identified for this project")
            
            # Recommended Team
            st.subheader("👨‍💻 Recommended Team")
            if selected_team:
                team_data = []
                from core_functions import score_employee
                for emp in selected_team:
                    score = score_employee(emp.get("skills", []), required_skills, emp.get("experience", 1))
                    team_data.append({
                        "Name": emp['name'],
                        "Skills": ", ".join(emp['skills']),
                        "Experience": f"{emp.get('experience', 1)} years",
                        "Match Score": f"{score}%"
                    })
                
                team_df = pd.DataFrame(team_data)
                st.dataframe(team_df, use_container_width=True, hide_index=True)
                
                # Team member cards
                st.write("**Team Members:**")
                cols = st.columns(len(selected_team))
                for i, (col, emp) in enumerate(zip(cols, selected_team)):
                    with col:
                        score = score_employee(emp.get("skills", []), required_skills, emp.get("experience", 1))
                        st.markdown(f"""
                        <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 5px solid #4CAF50; margin-bottom: 15px;'>
                            <h4 style='margin: 0 0 10px 0;'>{emp['name']}</h4>
                            <p style='margin: 5px 0;'><strong>Skills:</strong> {', '.join(emp['skills'])}</p>
                            <p style='margin: 5px 0;'><strong>Experience:</strong> {emp.get('experience', 1)} years</p>
                            <p style='margin: 5px 0;'><strong>Match:</strong> {score}%</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No suitable employees found for this project.")
            
            # Budget analysis
            st.subheader("💰 Budget Analysis")
            if estimated_cost <= budget:
                st.success(f"✅ Estimated cost (${estimated_cost:,.0f}) is within budget (${budget:,.0f})")
            else:
                st.error(f"❌ Estimated cost (${estimated_cost:,.0f}) exceeds budget (${budget:,.0f})")