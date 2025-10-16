# ai_advisor.py
import streamlit as st
from datetime import datetime
from utils import save_json
from ai_functions import get_ai_advice
from core_functions import score_employee

CHAT_FILE = "chat_history.json"

def render_ai_advisor():
    st.header("💬 AI Advisor - Skill Gap Solutions")
    
    if not st.session_state.projects:
        st.info("Analyze a project first to get AI advice")
    else:
        project_options = [p['name'] for p in st.session_state.projects]
        if project_options:
            selected_project_name = st.selectbox("Select Project for Advice", options=project_options)
            selected_project = next((p for p in st.session_state.projects if p['name'] == selected_project_name), None)
            
            if selected_project:
                st.write(f"**Project:** {selected_project['name']}")
                
                # Enhanced skill gap analysis
                st.subheader("🔍 Detailed Skill Analysis")
                
                # Calculate current skill gaps in real-time
                missing_skills = []
                coverage_percentage = 0
                
                if selected_project.get('required_skills'):
                    required_skills = selected_project['required_skills']
                    st.write(f"**Required Skills:**")
                    skills_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0;'>"
                    for skill in required_skills:
                        skills_html += f"<span style='background-color: #4CAF50; color: white; padding: 5px 12px; border-radius: 15px; font-size: 14px;'>{skill}</span>"
                    skills_html += "</div>"
                    st.markdown(skills_html, unsafe_allow_html=True)
                    
                    # Calculate current team skills
                    team_skills = set()
                    if selected_project.get('team'):
                        for emp in selected_project['team']:
                            team_skills.update(emp.get('skills', []))
                    
                    required_skills_set = set(required_skills)
                    missing_skills = list(required_skills_set - team_skills)
                    covered_skills = list(required_skills_set.intersection(team_skills))
                    coverage_percentage = round(len(covered_skills) / len(required_skills_set) * 100) if required_skills_set else 0
                    
                    # Display current team analysis
                    if selected_project.get('team'):
                        st.write(f"**Current Team Skills:** {', '.join(team_skills) if team_skills else 'No skills assigned'}")
                        st.write(f"**Skill Coverage:** {coverage_percentage}%")
                        
                        if missing_skills:
                            st.error(f"**Missing Skills:** {', '.join(missing_skills)}")
                            
                            # Show immediate solutions
                            st.subheader("🛠 Immediate Solutions")
                            for skill in missing_skills:
                                if skill in st.session_state.knowledge_base.get("skill_solutions", {}):
                                    solution_data = st.session_state.knowledge_base["skill_solutions"][skill]
                                    with st.expander(f"Solutions for {skill}", expanded=True):
                                        for i, solution in enumerate(solution_data.get("solutions", [])[:3]):
                                            st.write(f"**{i+1}. {solution}**")
                                        st.write(f"**Timeline Impact:** {solution_data.get('timeline_impact', 'Unknown')}")
                                        st.write(f"**Cost Impact:** {solution_data.get('cost_impact', 'Unknown')}")
                                        st.write(f"**Risk Level:** {solution_data.get('risk_level', 'Medium')}")
                        else:
                            st.success("✅ All required skills are covered by your current team.")
                    else:
                        st.warning("⚠ No team assigned to this project. Please build a team in the Team Builder tab first.")
                else:
                    st.error("❌ This project hasn't been properly analyzed. Please go to 'Project Analysis' tab and click 'Analyze Project & Build Team'")
                
                # Enhanced AI Advisor
                st.subheader("🤖 AI Project Advisor")
                
                # Dynamic question suggestions
                dynamic_suggestions = []
                if missing_skills:
                    dynamic_suggestions = [
                        f"How to handle missing {missing_skills[0]} skills?",
                        "What are cost-effective solutions for these skill gaps?",
                        "How will these gaps impact our timeline and budget?",
                        "Should we hire contractors or train our team?",
                        "What's the risk assessment for these missing skills?"
                    ]
                else:
                    dynamic_suggestions = [
                        "How can we optimize our current team further?",
                        "What training would benefit this project?",
                        "Any potential risks with our current skill set?",
                        "How to improve team productivity?",
                        "What emerging technologies should we consider?"
                    ]
                
                st.write("**Suggested Questions:**")
                cols = st.columns(2)
                for i, suggestion in enumerate(dynamic_suggestions):
                    with cols[i % 2]:
                        if st.button(suggestion, key=f"suggest_{i}", use_container_width=True):
                            st.session_state.current_question = suggestion
                            st.rerun()
                
                question = st.text_area(
                    "Ask specific questions about your project:",
                    value=st.session_state.current_question,
                    placeholder="e.g., How can we handle missing blockchain skills while staying within budget?",
                    key="question_input",
                    height=100
                )
                
                # Action buttons
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    if st.button("🚀 Get Detailed AI Analysis", type="primary", use_container_width=True):
                        if question.strip():
                            import os
                            # Verify API configuration
                            if not os.getenv("GEMINI_API_KEY"):
                                st.error("⚠ Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")
                                st.info("Using enhanced fallback recommendations instead...")
                            elif os.getenv("MODE", "gemini") != "gemini":
                                st.warning(f"⚠ MODE is set to '{os.getenv('MODE', 'gemini')}'. Change to 'gemini' in .env file to use AI.")
                                st.info("Using enhanced fallback recommendations instead...")
                            
                            with st.spinner("🤔 AI is analyzing your project..."):
                                advice = get_ai_advice(selected_project, question)
                                
                                # Display results
                                st.subheader("🎯 AI Recommendations")
                                st.markdown(advice)
                                
                                # Save to history
                                chat_entry = {
                                    "project": selected_project['name'],
                                    "question": question,
                                    "advice": advice,
                                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                    "missing_skills": missing_skills
                                }
                                st.session_state.chat_history.append(chat_entry)
                                save_json(CHAT_FILE, st.session_state.chat_history)
                                
                                st.session_state.current_question = ""
                        else:
                            st.warning("Please enter a question or select a suggestion.")
                
                with col2:
                    if st.button("🔄 Refresh Analysis", use_container_width=True):
                        st.info("Analysis refreshed! Check updated skill gaps above.")
                        st.rerun()
                
                with col3:
                    if st.button("📊 Project Summary", use_container_width=True):
                        with st.expander("Project Overview", expanded=True):
                            st.write(f"**Project:** {selected_project['name']}")
                            st.write(f"**Complexity:** {selected_project.get('complexity', 'Unknown')}")
                            st.write(f"**Team Size:** {len(selected_project.get('team', []))} members")
                            st.write(f"**Budget:** ${selected_project.get('budget', 0):,}")
                            st.write(f"**Timeline:** {selected_project.get('timeline', 0)} days")
                            st.write(f"**Skill Coverage:** {coverage_percentage}%")
                            if missing_skills:
                                st.write(f"**Critical Gaps:** {len(missing_skills)} skills")
                
                # Enhanced chat history
                if st.session_state.chat_history:
                    project_chats = [chat for chat in st.session_state.chat_history if chat.get('project') == selected_project['name']]
                    if project_chats:
                        st.subheader("📝 Conversation History")
                        for i, chat in enumerate(reversed(project_chats[-5:])):  # Show last 5 chats
                            with st.expander(f"💬 {chat.get('question', 'No question')[:70]}... ({chat.get('timestamp', 'No date')})", expanded=False):
                                advice_text = chat.get('advice') or chat.get('response', 'No advice available')
                                st.markdown(advice_text)
                                
                                # Show missing skills context
                                if chat.get('missing_skills'):
                                    st.caption(f"*Context: Missing skills - {', '.join(chat['missing_skills'])}*")