# analytics.py
import streamlit as st
import plotly.express as px

def render_analytics():
    st.header("📈 Analytics Dashboard")
    
    if st.session_state.projects:
        # Project metrics
        st.subheader("Project Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Projects", len(st.session_state.projects))
        with col2:
            total_cost = sum(p.get('estimated_cost', 0) for p in st.session_state.projects)
            st.metric("Total Estimated Cost", f"${total_cost:,.0f}")
        with col3:
            avg_team_size = sum(p.get('team_size', 0) for p in st.session_state.projects) / len(st.session_state.projects)
            st.metric("Avg Team Size", round(avg_team_size, 1))
        
        # Project list
        st.subheader("Projects")
        for i, project in enumerate(st.session_state.projects):
            with st.expander(f"{i+1}. {project['name']} - ${project.get('estimated_cost', 0):,.0f}"):
                st.write(f"**Summary:** {project.get('summary', 'No summary')}")
                st.write(f"**Team:** {', '.join([e['name'] for e in project.get('team', [])])}")
                st.write(f"**Timeline:** {project.get('timeline', 0)} days")
                st.write(f"**Complexity:** {project.get('complexity', 'Unknown')}")
                if project.get('skill_gaps'):
                    st.write(f"**Skill Coverage:** {project['skill_gaps'].get('coverage_percentage', 0)}%")
        
        # Cost comparison chart
        st.subheader("Project Cost Comparison")
        project_names = [p['name'] for p in st.session_state.projects]
        project_costs = [p.get('estimated_cost', 0) for p in st.session_state.projects]
        if project_costs:
            fig = px.bar(x=project_names, y=project_costs, title="Project Costs")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No projects yet. Analyze a project to see analytics here.")