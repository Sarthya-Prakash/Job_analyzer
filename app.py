import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import difflib

def get_jobs(query):
    url = "https://jsearch.p.rapidapi.com/search"

    querystring = {
        "query": query,
        "page": "1",
        "num_pages": "1"
    }

    headers = {
        "X-RapidAPI-Key": "adf06cba27mshb184790183c6e70p1d2282jsnc4f6605c02c9",
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response.json()


def extract_skills(text, skills):
    text = str(text).lower()
    return [skill for skill in skills if skill in text]


#  UI
st.title(" Job Market Analyzer")

query = st.text_input("Enter Job Role", "data analyst india")
skill_input = st.text_input("Enter Skills (comma-separated)", "python, sql, excel")

if st.button("Analyze Jobs"):

    valid_skills_master = [
    "python", "sql", "excel", "tableau", "power bi",
    "machine learning", "statistics", "pandas", "numpy",
    "java", "html", "css", "javascript", "react", "react js"
]

    skills_list = [s.strip().lower() for s in skill_input.split(",")]

    invalid_skills = [s for s in skills_list if s not in valid_skills_master]

    if invalid_skills:
        st.warning(f" Invalid skills: {', '.join(invalid_skills)}")

        for skill in invalid_skills:
            match = difflib.get_close_matches(skill, valid_skills_master, n=1)
            if match:
                st.info(f" Did you mean '{match[0]}' instead of '{skill}'?")

    skills_list = [s for s in skills_list if s in valid_skills_master]

    if not skills_list:
        st.error(" No valid skills to analyze")
        st.stop()

    data = get_jobs(query)

    jobs = []

    for job in data.get("data", []):
        desc = job.get("job_description")

        jobs.append({
            "Title": job.get("job_title"),
            "Company": job.get("employer_name"),
            "Location": job.get("job_city"),
            "Skills": extract_skills(desc, skills_list)
        })

    df = pd.DataFrame(jobs)

    if df.empty:
        st.error("No job data found")
        st.stop()

    st.subheader(" Job Data")
    st.dataframe(df)

    
    all_skills = []
    for s in df['Skills']:
        all_skills.extend(s)

    if not all_skills:
        st.warning(" No matching skills found")
        st.stop()

    skill_counts = Counter(all_skills)
    skill_df = pd.DataFrame(skill_counts.items(), columns=['Skill', 'Count'])

   
    col1, col2 = st.columns(2)
    col1.metric("Total Jobs", len(df))
    col2.metric("Top Skill", skill_df.sort_values(by='Count', ascending=False).iloc[0]['Skill'])

    
    st.subheader(" Skill Demand")

    fig1, ax1 = plt.subplots()
    sns.barplot(x='Skill', y='Count', data=skill_df,color="#9F006D", ax=ax1)
    ax1.set_title("Most In-Demand Skills")
    for bars in ax1.containers:
        ax1.bar_label(bars)
    st.pyplot(fig1)

    if len(skill_df) <= 6:
        st.subheader(" Skill Distribution")

        fig2, ax2 = plt.subplots()
        ax2.pie(skill_df['Count'], labels=skill_df['Skill'], autopct='%1.1f%%')
        ax2.set_title("Skill Share")
        st.pyplot(fig2)

    st.subheader(" Skill Correlation Heatmap")

    for skill in skills_list:
        df[skill] = df['Skills'].apply(lambda x: 1 if skill in x else 0)

    fig3, ax3 = plt.subplots()
    sns.heatmap(df[skills_list].corr(), annot=True, cmap="inferno", ax=ax3)
    ax3.set_title("Skill Correlation")
    st.pyplot(fig3)

    st.subheader(" Job Locations Analysis")

    location_df = df['Location'].value_counts().reset_index()
    location_df.columns = ['Location', 'Count']

    
    fig4, ax4 = plt.subplots()
    sns.barplot(x='Count', y='Location', data=location_df,color="#EEF606", ax=ax4)
    ax4.set_title("Jobs by Location")
    for bars in ax4.containers:
        ax4.bar_label(bars)
    st.pyplot(fig4)

    
    st.subheader(" Location Heatmap (Density)")

    
    location_matrix = pd.DataFrame(location_df)

    fig5, ax5 = plt.subplots()
    sns.heatmap(location_matrix[['Count']], annot=True, cmap="magma", yticklabels=location_matrix['Location'], ax=ax5)
    ax5.set_title("Job Density by Location")
    st.pyplot(fig5)