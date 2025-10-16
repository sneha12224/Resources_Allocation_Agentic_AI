# ai_functions.py
import streamlit as st
import json
import re
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
MODE = os.getenv("MODE", "gemini")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Configure API
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

def call_gemini(prompt):
    """Return raw text from Gemini or error text"""
    if not GEMINI_KEY or MODE != "gemini":
        return "_NO_GEMINI_"
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")  # Updated model name
        resp = model.generate_content(prompt)
        
        # Check if response has text
        if hasattr(resp, 'text') and resp.text:
            return resp.text
        elif hasattr(resp, 'parts') and resp.parts:
            return resp.parts[0].text
        else:
            return "_ERROR_ No text in response"
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return f"_ERROR_ Gemini call failed: {e}"

def parse_json_or_try_fix(raw_str):
    try:
        return json.loads(raw_str)
    except Exception:
        m = re.search(r"\{.*\}", raw_str, re.S)
        if m:
            candidate = m.group(0)
            try:
                return json.loads(candidate)
            except Exception:
                pass
        return None

def call_gemini_json(prompt):
    """Ask Gemini and try to parse JSON reply. Return parsed_obj or None plus raw text."""
    raw = call_gemini(prompt)
    parsed = parse_json_or_try_fix(raw)
    return parsed, raw

def predict_project_summary(project_description):
    """AI predicts project summary"""
    prompt = f"""
    Create a concise 2-3 sentence summary of this project description. 
    Return ONLY the summary text without any additional commentary.
    
    Project: {project_description}
    
    Focus on the main goal, key features, and intended outcome.
    """
    
    if MODE == "gemini" and GEMINI_KEY:
        response = call_gemini(prompt)
        # Clean the response
        if response and not response.startswith("_"):
            return response.strip()
    
    # Fallback summary
    sentences = project_description.split('.')
    if len(sentences) > 2:
        return '. '.join(sentences[:2]) + '.'
    return project_description[:200] + "..."

def extract_technologies_from_text(text):
    """Extract technologies from text using keyword matching"""
    tech_keywords = {
        "Python": ["python", "django", "flask"],
        "JavaScript": ["javascript", "js", "node", "react", "angular", "vue"],
        "Java": ["java", "spring", "hibernate"],
        "C#": ["c#", ".net", "asp.net"],
        "PHP": ["php", "laravel", "wordpress"],
        "Database": ["mysql", "postgresql", "mongodb", "sql", "database"],
        "AWS": ["aws", "amazon web services"],
        "Azure": ["azure", "microsoft cloud"],
        "Docker": ["docker", "container"],
        "Kubernetes": ["kubernetes", "k8s"],
        "React": ["react", "react.js"],
        "Vue": ["vue", "vue.js"],
        "Angular": ["angular"],
        "Blockchain": ["blockchain", "ethereum", "solidity", "smart contract"],
        "AI/ML": ["ai", "machine learning", "ml", "tensorflow", "pytorch", "neural network"],
        "Mobile": ["ios", "android", "flutter", "react native"],
        "Security": ["security", "encryption", "authentication", "cybersecurity"],
        "Cloud": ["cloud", "aws", "azure", "google cloud", "cloud computing"],
        "Go": ["go", "golang"],
        "Golang": ["golang", "go language"]
    }
    
    text_lower = text.lower()
    detected_tech = set()
    
    for tech, keywords in tech_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected_tech.add(tech)
                break
    
    return list(detected_tech)[:8]  # Return max 8 technologies

def predict_project_parameters(project_description):
    """AI predicts complexity, team size, and budget based on project description"""
    prompt = f"""
    Analyze this project description and predict realistic parameters.
    Return ONLY valid JSON without any additional text.
    
    Project: {project_description}
    
    Consider factors like technical complexity, scope size, industry standards, and typical team sizes for similar projects.
    
    Guidelines for team size:
    - Small simple projects: 1-2 people
    - Medium complexity: 3-4 people  
    - Complex projects: 5-6 people
    - Very complex/enterprise: 7-10 people
    
    Guidelines for budget:
    - Small project: $5,000-$15,000
    - Medium project: $15,000-$50,000
    - Large project: $50,000-$150,000
    - Enterprise: $150,000+
    
    Return format:
    {{
      "summary": "brief project summary",
      "complexity": "low/medium/high/very high",
      "recommended_team_size": 3,
      "estimated_budget": 15000,
      "timeline_weeks": 12,
      "risk_level": "low/medium/high",
      "key_technologies": ["tech1", "tech2", "tech3"]
    }}
    """
    
    if MODE == "gemini" and GEMINI_KEY:
        parsed, raw = call_gemini_json(prompt)
        if parsed:
            # Validate the parsed data
            if "recommended_team_size" in parsed:
                # Ensure team size is within reasonable bounds
                parsed["recommended_team_size"] = max(1, min(10, parsed["recommended_team_size"]))
            return parsed
    
    # Fallback predictions with better logic
    text_lower = project_description.lower()
    
    # Improved complexity detection
    complexity = "medium"
    if any(word in text_lower for word in ["simple", "basic", "small", "minimal", "landing page", "brochure"]):
        complexity = "low"
    elif any(word in text_lower for word in ["complex", "enterprise", "large-scale", "mission critical", "banking", "healthcare"]):
        complexity = "high"
    elif any(word in text_lower for word in ["blockchain", "ai", "machine learning", "iot", "advanced", "sophisticated"]):
        complexity = "very high"
    
    # Improved team size prediction based on complexity
    team_sizes = {"low": 2, "medium": 3, "high": 5, "very high": 7}
    team_size = team_sizes.get(complexity, 3)
    
    # Improved budget estimation
    budgets = {"low": 10000, "medium": 25000, "high": 75000, "very high": 150000}
    budget = budgets.get(complexity, 25000)
    
    # Improved timeline estimation
    timelines = {"low": 4, "medium": 8, "high": 16, "very high": 24}
    timeline_weeks = timelines.get(complexity, 8)
    
    # Improved risk assessment
    risk_level = "medium"
    if complexity in ["high", "very high"]:
        risk_level = "high"
    elif complexity == "low":
        risk_level = "low"
    
    return {
        "summary": predict_project_summary(project_description),
        "complexity": complexity,
        "recommended_team_size": team_size,
        "estimated_budget": budget,
        "timeline_weeks": timeline_weeks,
        "risk_level": risk_level,
        "key_technologies": extract_technologies_from_text(project_description)
    }

def predict_required_skills(project_description):
    """Predict required skills for a project using AI"""
    prompt = f"""
    Analyze this project description and extract ALL required technical skills. 
    Return ONLY a JSON array of skill names without any additional text.
    
    Project: {project_description}
    
    Return format: ["Skill1", "Skill2", "Skill3", "Skill4", "Skill5", "Skill6"...]
    """
    
    if MODE == "gemini" and GEMINI_KEY:
        raw = call_gemini(prompt)
        try:
            skills_match = re.search(r'\[.*\]', raw)
            if skills_match:
                skills = json.loads(skills_match.group())
                return skills
        except:
            pass
    
    # Fallback: Extract skills using keyword matching
    return extract_skills_from_text(project_description)

def extract_skills_from_text(text):
    """Extract skills from text using keyword matching"""
    skill_keywords = {
        "Python": ["python", "django", "flask"],
        "AI/ML": ["ai", "machine learning", "ml", "tensorflow", "pytorch", "neural network"],
        "React": ["react", "frontend", "ui"],
        "JavaScript": ["javascript", "js", "node"],
        "Database": ["sql", "mysql", "mongodb", "database"],
        "DevOps": ["devops", "aws", "docker", "kubernetes"],
        "Blockchain": ["blockchain", "smart contract", "solidity", "ethereum"],
        "Security": ["security", "encryption", "authentication", "cybersecurity"],
        "Cloud": ["aws", "azure", "google cloud", "cloud"],
        "Go": ["go", "golang"],
        "Golang": ["golang", "go language"]
    }
    
    text_lower = text.lower()
    detected_skills = set()
    
    for skill, keywords in skill_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected_skills.add(skill)
                break
    
    return list(detected_skills)

def get_ai_advice(project, question):
    """Get AI advice for skill gaps and project challenges - FIXED VERSION"""
    # Calculate current skill gaps
    missing_skills = []
    
    if project.get('skill_gaps') and project['skill_gaps'].get('missing_skills'):
        missing_skills = project['skill_gaps']['missing_skills']
    else:
        # Calculate current skill gaps from assigned team
        if project.get('team') and project.get('required_skills'):
            team_skills = set()
            for emp in project['team']:
                team_skills.update(emp.get('skills', []))
            required_skills_set = set(project['required_skills'])
            missing_skills = list(required_skills_set - team_skills)
    
    if not missing_skills:
        return "## AI Analysis\n\nNo significant skill gaps identified for this project. The current team appears to have all the necessary skills for successful project delivery."
    
    # Build comprehensive project context
    project_context = f"""
Project Name: {project['name']}
Description: {project.get('description', 'No description')}
Summary: {project.get('summary', 'No summary')}

CRITICAL MISSING SKILLS: {', '.join(missing_skills)}
Available Team Skills: {', '.join([s for emp in project.get('team', []) for s in emp.get('skills', [])])}
Required Skills: {', '.join(project.get('required_skills', []))}

Team Size: {len(project.get('team', []))} members
Budget: ${project.get('budget', 0):,}
Estimated Cost: ${project.get('estimated_cost', 0):,}
Timeline: {project.get('timeline', 0)} days
Complexity: {project.get('complexity', 'Unknown')}
Risk Level: {project.get('risk_level', 'Unknown')}

User Question: {question}
"""
    
    prompt = f"""You are a senior project management consultant with 15+ years of experience in technology consulting and team building.

CONTEXT:
{project_context}

TASK: Provide SPECIFIC, ACTIONABLE advice for handling the missing skills and answering the user's question.

Your response MUST include:

1. **Immediate Action Items** (What to do THIS WEEK)
   - Specific steps to address each missing skill
   - Who to contact, what to post, where to search

2. **Cost-Effective Solutions** (with actual numbers)
   - Hiring costs (hourly rates, total estimates)
   - Training costs (programs, duration, pricing)
   - Outsourcing options (vendors, pricing models)

3. **Timeline Impact Analysis**
   - How each solution affects the delivery date
   - Critical path items
   - Dependencies and risks

4. **Risk Assessment**
   - Specific risks for each missing skill
   - Mitigation strategies
   - Contingency plans

5. **Recommended Approach**
   - Your #1 recommended solution with full justification
   - Step-by-step implementation plan
   - Success metrics

Format your response in clear markdown with headers (##) and bullet points.
Be SPECIFIC - avoid generic advice. Give actual numbers, timelines, and actionable steps.
"""
    
    # Try to get AI response
    if MODE == "gemini" and GEMINI_KEY:
        try:
            response = call_gemini(prompt)
            
            # Check if we got a valid response
            if response and not response.startswith("_ERROR_") and not response.startswith("_NO_GEMINI_"):
                # Clean up the response
                response = response.strip()
                if len(response) > 100:  # Valid response should be substantial
                    return response
        except Exception as e:
            st.error(f"Error calling Gemini API: {str(e)}")
    
    # Enhanced fallback advice
    fallback_advice = ["## AI Project Advisor - Comprehensive Solutions\n"]
    
    if missing_skills:
        fallback_advice.append("### Critical Skill Gap Analysis")
        fallback_advice.append(f"**Missing Skills:** {', '.join(missing_skills)}")
        fallback_advice.append(f"**Impact Level:** {'High' if len(missing_skills) > 2 else 'Medium'}")
        fallback_advice.append(f"**Urgency:** {'Immediate action required' if len(missing_skills) > 2 else 'Address within 1-2 weeks'}")
        fallback_advice.append("")
        
        fallback_advice.append("### Specific Solutions by Skill\n")
        
        for skill in missing_skills:
            # Find matching solution data
            solution_data = None
            for skill_key in [skill, skill.lower(), skill.capitalize()]:
                if skill_key in st.session_state.knowledge_base.get("skill_solutions", {}):
                    solution_data = st.session_state.knowledge_base["skill_solutions"][skill_key]
                    break
            
            if solution_data:
                fallback_advice.append(f"#### {skill} Solutions\n")
                
                for i, sol in enumerate(solution_data.get("solutions", [])[:4], 1):
                    fallback_advice.append(f"**Option {i}:** {sol}")
                
                fallback_advice.append(f"\n**Impact:**")
                fallback_advice.append(f"- Timeline: {solution_data.get('timeline_impact', '2-4 weeks')}")
                fallback_advice.append(f"- Cost: {solution_data.get('cost_impact', '$10k-25k')}")
                fallback_advice.append(f"- Risk: {solution_data.get('risk_level', 'Medium')}\n")
            else:
                fallback_advice.append(f"#### {skill} Solutions\n")
                fallback_advice.append(f"**Specialized skill requiring custom approach:**")
                fallback_advice.append(f"1. Hire senior {skill} developer ($120-180/hr)")
                fallback_advice.append(f"2. 4-6 week training program for existing team ($8k-15k)")
                fallback_advice.append(f"3. Contract with {skill} consulting firm")
                fallback_advice.append(f"4. Evaluate alternative technologies\n")
        
        fallback_advice.append("### Recommended Implementation Strategy\n")
        fallback_advice.append("#### Week 1-2: Immediate Actions")
        fallback_advice.append("- Post job listings for critical skills")
        fallback_advice.append("- Contact 3-5 recruiting agencies")
        fallback_advice.append("- Research training programs")
        fallback_advice.append("- Get quotes from consulting firms\n")
        
        fallback_advice.append("#### Week 3-4: Team Building")
        fallback_advice.append("- Interview and hire top contractors")
        fallback_advice.append("- Enroll team in training programs")
        fallback_advice.append("- Set up mentorship with contractors\n")
        
        fallback_advice.append("#### Week 5+: Execution")
        fallback_advice.append("- Begin knowledge transfer")
        fallback_advice.append("- Regular skill assessments")
        fallback_advice.append("- Adjust strategy based on progress\n")
        
        fallback_advice.append("### Budget Impact Summary\n")
        estimated_cost = len(missing_skills) * 20000
        fallback_advice.append(f"- **Additional Budget Needed:** ${estimated_cost:,} - ${estimated_cost + 30000:,}")
        fallback_advice.append(f"- **Timeline Extension:** {len(missing_skills) * 3}-{len(missing_skills) * 5} weeks")
        fallback_advice.append(f"- **ROI Timeline:** 3-6 months\n")
        
        fallback_advice.append("### #1 Recommended Approach\n")
        fallback_advice.append("**Hybrid Strategy:** Hire 1-2 senior contractors immediately while training your existing team in parallel.")
        fallback_advice.append("\n**Why this works:**")
        fallback_advice.append("- Immediate capability (contractors)")
        fallback_advice.append("- Long-term sustainability (trained team)")
        fallback_advice.append("- Knowledge transfer built-in")
        fallback_advice.append("- Cost-effective over time")
    
    return "\n".join(fallback_advice)