# employee_database.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_employee_database():
    st.header("📊 Employee Database")
    
    if st.session_state.employees:
        # Convert to DataFrame for better display
        emp_data = []
        for emp in st.session_state.employees:
            emp_data.append({
                "Name": emp['name'],
                "Skills": ", ".join(emp['skills']),
                "Experience": f"{emp.get('experience', 1)} years",
                "Workload": f"{emp.get('workload', 0)}%"
            })
        
        df = pd.DataFrame(emp_data)
        st.dataframe(df, use_container_width=True)
        
        # Skills visualization
        st.subheader("Skills Distribution")
        all_skills = [skill for emp in st.session_state.employees for skill in emp['skills']]
        if all_skills:
            skill_counts = pd.Series(all_skills).value_counts()
            fig = px.bar(skill_counts, title="Skills Across Employees", 
                        labels={'index': 'Skill', 'value': 'Count'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No skills data available for visualization")
    else:
        st.info("No employees in database. Add some employees first.")