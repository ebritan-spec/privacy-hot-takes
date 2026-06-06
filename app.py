import streamlit as st
import requests
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Privacy Hot Takes", layout="wide")
st.title("🔒 Daily Privacy Hot Takes Generator")

# ===================== API KEYS =====================
if "SERPER_API_KEY" not in os.environ:
    serper_key = st.text_input("Enter your Serper API Key", type="password")
    openai_key = st.text_input("Enter your OpenAI API Key", type="password")
    
    if serper_key and openai_key:
        os.environ["SERPER_API_KEY"] = serper_key
        os.environ["OPENAI_API_KEY"] = openai_key
        st.success("Keys saved for this session!")
# ===================================================

def search_recent_privacy_issues():
    # 1. Try getting the key from your on-screen inputs first, fallback to environment
    api_key = st.session_state.get('serper_api_key') or os.environ.get("SERPER_API_KEY")
    
    # 2. A simpler, highly reliable query that doesn't expire every 3 days
    query = '("data privacy" OR GDPR OR CCPA OR "AI privacy" OR "data protection") (breach OR regulation OR fine OR controversy)'
    
    payload = {"q": query, "num": 10}
    headers = {
        'X-API-KEY': api_key, 
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post("https://google.serper.dev/search", json=payload, headers=headers, timeout=10)
        results = response.json().get("organic", [])
        
        articles = []
        for r in results:
            title = r.get('title', 'No Title')
            snippet = r.get('snippet', '')
            link = r.get('link', '#')
            articles.append(f"**{title}**\n{snippet}\n[Link]({link})\n")
            
        return "\n---\n".join(articles) if articles else "No recent results found."
    except Exception as e:
        return f"Error connecting to search. Please check your Serper key. Details: {e}"

def generate_hot_takes(issues):
    prompt = f"""
You are a sharp privacy thought leader at Salesforce. Create 4 bold, discussion-provoking hot takes for business and social events.

Recent issues:
{issues}

Rules:
- Each take should be 1-2 sentences
- Witty, authoritative, slightly edgy
- Include a contrarian angle or interesting tension
- End each take with a question to spark debate
"""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating takes: {str(e)}"

# ===================== MAIN =====================
if st.button("🚀 Generate Today's Privacy Hot Takes", type="primary"):
    with st.spinner("Searching recent issues and generating hot takes..."):
        issues_text = search_recent_privacy_issues()
        
        st.subheader("📌 Recent Privacy Issues")
        st.markdown(issues_text)
        
        st.subheader("🎯 Generated Hot Takes")
        takes = generate_hot_takes(issues_text)
        st.markdown(takes)

st.caption("Privacy Hot Takes Tool • Built for quick daily use")