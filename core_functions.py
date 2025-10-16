# core_functions.py
def score_employee(emp_skills, req_skills, emp_experience=1):
    if not req_skills:
        return 0
    
    emp_lower = [s.lower() for s in emp_skills]
    req_lower = [s.lower() for s in req_skills]
    
    match_count = 0
    for req_skill in req_lower:
        for emp_skill in emp_lower:
            if req_skill in emp_skill or emp_skill in req_skill:
                match_count += 1
                break
    
    base_score = round(match_count / len(req_lower) * 100)
    experience_bonus = min(emp_experience * 5, 20)
    return min(base_score + experience_bonus, 100)

def build_optimal_team(required_skills, employees, team_size=3):
    """Build optimal team based on required skills"""
    scored_employees = []
    
    for emp in employees:
        score = score_employee(emp.get("skills", []), required_skills, emp.get("experience", 1))
        scored_employees.append({
            "employee": emp,
            "score": score,
            "experience": emp.get("experience", 1)
        })
    
    scored_employees.sort(key=lambda x: (-x["score"], -x["experience"]))
    selected_team = [item["employee"] for item in scored_employees[:team_size]]
    
    return selected_team, scored_employees

def calculate_project_timeline(complexity, team_size):
    base_days = {"low": 15, "medium": 30, "high": 60, "very high": 90}
    adjustment = max(1, 5 - team_size * 0.5)
    return round(base_days.get(complexity, 30) / adjustment)

def estimate_project_cost(team, timeline):
    daily_rates = {
        "Python": 500, "AI/ML": 700, "React": 550, "JavaScript": 550,
        "Database": 500, "DevOps": 600, "Blockchain": 800, "Security": 650,
        "Cloud": 600, "Design": 450, "Go": 650, "Golang": 650
    }
    
    total_cost = 0
    for emp in team:
        emp_skills = emp.get("skills", [])
        if emp_skills:
            avg_rate = sum(daily_rates.get(skill, 450) for skill in emp_skills) / len(emp_skills)
            total_cost += avg_rate * timeline
    
    return round(total_cost)

def analyze_skill_gaps(required_skills, available_employees):
    """Analyze gaps between required skills and available team"""
    available_skills = set()
    for emp in available_employees:
        available_skills.update(emp.get("skills", []))
    
    required_set = set(required_skills)
    missing_skills = required_set - available_skills
    covered_skills = required_set.intersection(available_skills)
    
    return {
        "missing_skills": list(missing_skills),
        "covered_skills": list(covered_skills),
        "coverage_percentage": round(len(covered_skills) / len(required_set) * 100) if required_set else 0
    }