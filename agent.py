import streamlit as st
import PyPDF2
import pandas as pd
import json
import os
from groq import Groq
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. PAGE SETUP & HIGH-CONTRAST STYLING
st.set_page_config(
    page_title="AI Resume Intelligence Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Global App Background */
    .stApp { background-color: #07090e; }
    
    /* FORCE SIDEBAR BACKGROUND & TEXT */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Force ALL standard text, labels, and markdown to bright white */
    body, label, span, p, div, .stMarkdown, .stCaption {
        color: #ffffff !important;
    }
    
    /* Custom HTML Headings */
    .section-title {
        color: #ffffff !important;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    /* Ultimate Header Banner */
    .app-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
        padding: 3rem;
        border-radius: 20px;
        border: 1px solid rgba(147, 197, 253, 0.3);
        margin-bottom: 2.5rem;
        box-shadow: 0 25px 50px -12px rgba(49, 16, 66, 0.5);
    }
    .app-title { 
        font-size: 3rem; 
        font-weight: 900; 
        margin: 0; 
        letter-spacing: -1px; 
        background: linear-gradient(90deg, #60a5fa, #c084fc, #f472b6); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
    }
    .app-subtitle { font-size: 1.2rem; color: #cbd5e1 !important; margin-top: 0.8rem; font-weight: 400; line-height: 1.5; }
    
    /* Ultimate Glowing Buttons */
    .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        box-shadow: 0 6px 25px rgba(139, 92, 246, 0.7) !important;
    }
    
    /* Tech Stack Badges */
    .badge {
        display: inline-block;
        padding: 0.4rem 0.9rem;
        font-size: 0.85rem;
        font-weight: 600;
        border-radius: 8px;
        background-color: #172033;
        color: #93c5fd !important;
        border: 1px solid rgba(147, 197, 253, 0.4);
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Sidebar Command Styling */
    .sidebar-card {
        background: #141c2e;
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        margin-bottom: 1rem;
    }
    .status-online {
        display: inline-block;
        width: 9px;
        height: 9px;
        background-color: #10b981;
        border-radius: 50%;
        margin-right: 8px;
        box-shadow: 0 0 12px #10b981;
    }
    
    /* Text Inputs */
    .stTextArea textarea {
        background-color: #0e1422 !important;
        color: #ffffff !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    /* File Uploader Container */
    [data-testid="stFileUploader"] {
        background-color: #0e1422 !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }
    [data-testid="stFileUploader"] section {
        background-color: #141c2e !important;
        border: 2px dashed rgba(147, 197, 253, 0.4) !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: none !important;
    }
    
    /* COMPLETELY REMOVE WHITE BACKGROUND IN UPLOADED FILE PILLS / TAGS */
    [data-baseweb="tag"], div[data-baseweb="tag"], span[data-baseweb="tag"] {
        background-color: #172033 !important;
        border: 1px solid rgba(147, 197, 253, 0.4) !important;
    }
    [data-baseweb="tag"] * , div[data-baseweb="tag"] * {
        background-color: transparent !important;
        color: #ffffff !important;
        fill: #ffffff !important;
    }
    
    /* Alerts and Error Box Background Fix */
    .stAlert, div[data-baseweb="notification"], div[role="alert"] {
        background-color: #141c2e !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: #ffffff !important;
    }
    .stAlert *, div[data-baseweb="notification"] *, div[role="alert"] * {
        color: #ffffff !important;
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE FOR RESET BUTTON ---
if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

def reset_app():
    st.session_state.reset_counter += 1

# 2. LOAD API KEY
load_dotenv()
try:
    api_key = os.environ.get("GROQ_API_KEY")
    client = Groq(api_key=api_key)
except Exception as e:
    st.error("⚠️ Failed to load Groq API Key. Please make sure GROQ_API_KEY is saved in your .env file!")

# --- Core Functions ---
def extract_text_from_upload(uploaded_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "
    except Exception as e:
        return ""
    return text.strip()

def evaluate_single_candidate(uploaded_file, jd_text):
    resume_text = extract_text_from_upload(uploaded_file)
    if not resume_text:
        return None
        
    prompt = f"""
    You are an elite Chief Technology Officer and Lead Technical Recruiter. Perform an ultra-precise, objective evaluation of the candidate's resume against the Job Description.
    
    JOB DESCRIPTION:
    {jd_text}
    
    RESUME TEXT:
    {resume_text}
    
    Evaluate across these exact pillars and output STRICTLY a JSON object with these keys:
    1. "score": An integer from 0 to 100 calculated precisely based on weighted breakdown (Skills: 40%, Experience: 30%, Education: 15%, Relevance: 15%).
    2. "skills_match_score": Integer (0-100) reflecting tech stack alignment.
    3. "experience_match_score": Integer (0-100) reflecting professional background or project relevance.
    4. "skills": A flat list of technical skills found in the resume.
    5. "experience": A short 1-sentence summary of total background/experience.
    6. "education": Highest degree qualification.
    7. "verdict": One of exactly three strings: "🔥 Strong Hire", "⚠️ Moderate Fit", or "❌ Low Fit".
    8. "reasoning": 2 precise sentences outlining exact matching strengths and missing gaps.
    
    Return ONLY a valid JSON object.
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Execute ultra-precision matrix scoring."}
            ],
            temperature=0.05 
        )
        ai_data = json.loads(response.choices[0].message.content)
        
        return {
            "Candidate": uploaded_file.name,
            "Score": int(ai_data.get("score", 0)),
            "Skills Score": int(ai_data.get("skills_match_score", 0)),
            "Experience Score": int(ai_data.get("experience_match_score", 0)),
            "Verdict": ai_data.get("verdict", "⚠️ Moderate Fit"),
            "Reasoning": ai_data.get("reasoning", "No evaluation notes provided."),
            "Experience": ai_data.get("experience", "See resume"),
            "Education": ai_data.get("education", "See resume"),
            "Skills": ai_data.get("skills", [])
        }
    except Exception as e:
        return {
            "Candidate": uploaded_file.name,
            "Score": 0,
            "Skills Score": 0,
            "Experience Score": 0,
            "Verdict": "❌ Low Fit",
            "Reasoning": f"Evaluation error: {str(e)}",
            "Experience": "N/A",
            "Education": "N/A",
            "Skills": []
        }

# --- ULTIMATE SIDEBAR CONTROL CENTER ---
with st.sidebar:
    st.markdown("<p style='color: #ffffff !important; font-size: 1.3rem; font-weight: 800;'>⚡ Command Hub</p>", unsafe_allow_html=True)
    st.markdown("<p style='color: #cbd5e1 !important;'>Enterprise Recruitment Matrix</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("""
    <div class="sidebar-card">
        <span style="font-size: 0.75rem; color: #93c5fd !important; font-weight: 700; text-transform: uppercase;">Engine Status</span>
        <div style="font-size: 0.95rem; font-weight: 700; color: #ffffff !important; margin-top: 6px;">
            <span class="status-online"></span>Parallel High-Speed Mode Active
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sidebar-card">
        <span style="font-size: 0.75rem; color: #93c5fd !important; font-weight: 700; text-transform: uppercase;">System Architect</span>
        <div style="font-size: 0.95rem; font-weight: 700; color: #ffffff !important; margin-top: 6px;">👨‍💻 Thrishal</div>
        <div style="font-size: 0.8rem; color: #cbd5e1 !important; margin-top: 3px;">Version 1.0.0 • Multi-threaded</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<p style='color: #ffffff !important; font-weight: 700;'>🛠️ Quick Actions</p>", unsafe_allow_html=True)
    if st.button("🔄 Reset Workspace", use_container_width=True):
        reset_app()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.info("💡 **Pro-Tip:** Upload up to 10+ PDFs simultaneously. Multi-threaded processing analyzes all resumes concurrently in seconds.")

# --- MAIN HERO BANNER ---
st.markdown("""
<div class="app-header">
    <p class="app-title">⚡ AI Resume Intelligence Suite</p>
    <p class="app-subtitle">High-speed parallel processing engine, multi-pillar weighted matrix evaluation, and instant candidate ranking.</p>
</div>
""", unsafe_allow_html=True)

# --- APP TABS ---
tab1, tab2 = st.tabs(["📄 Resume Evaluation Engine", "💬 Autonomous HR Assistant"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">📝 1. Job Description</p>', unsafe_allow_html=True)
        jd_input = st.text_area(
            "Paste the target role requirements here:", 
            height=190, 
            placeholder="e.g. Looking for an Android developer experienced in Kotlin, Jetpack Compose, and offline-first databases...",
            key=f"jd_{st.session_state.reset_counter}"
        )

    with col2:
        st.markdown('<p class="section-title">📎 2. Candidate Resumes</p>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "Upload candidate resumes (PDF format)", 
            type=['pdf'], 
            accept_multiple_files=True, 
            key=f"uploader_{st.session_state.reset_counter}"
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("⚡ Run High-Speed Parallel Evaluation", use_container_width=True):
        if not uploaded_files:
            st.warning("⚠️ Please upload at least one candidate resume PDF.")
        elif len(jd_input.strip()) < 20:
            st.warning("⚠️ Please paste a more detailed job description.")
        else:
            results = []
            with st.spinner(f'🚀 Processing {len(uploaded_files)} resumes concurrently using multi-threading...'):
                with ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_file = {
                        executor.submit(evaluate_single_candidate, file, jd_input): file 
                        for file in uploaded_files
                    }
                    
                    for future in as_completed(future_to_file):
                        res = future.result()
                        if res:
                            results.append(res)
            
            if results:
                st.success(f"✅ Successfully evaluated {len(results)} candidate(s) in record time!")
                df = pd.DataFrame(results)
                df = df.sort_values(by="Score", ascending=False)
                
                st.markdown("---")
                st.markdown('<p style="color: #ffffff !important; font-size: 1.5rem; font-weight: 800;">🏆 Ranked Leaderboard</p>', unsafe_allow_html=True)
                
                # --- CLEAN STREAMLIT CONTAINER CARDS ---
                for index, row in df.iterrows():
                    score = row['Score']
                    verdict = row['Verdict']
                    candidate_name = row['Candidate']
                    
                    with st.container():
                        st.markdown(f"""
                        <div style="background: #0e1422; padding: 2rem; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.2); box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.8); margin-bottom: 1.8rem;">
                            <h3 style="margin: 0 0 1rem 0; color: #ffffff !important; font-size: 1.4rem;">👤 {candidate_name}</h3>
                        """, unsafe_allow_html=True)
                        
                        col_metrics, col_info = st.columns([1, 3])
                        with col_metrics:
                            st.metric(label="Overall Accuracy", value=f"{score}/100")
                            st.progress(int(score))
                            st.caption(f"🛠️ Tech Match: {row['Skills Score']}%")
                            st.caption(f"💼 Exp Match: {row['Experience Score']}%")
                            st.markdown(f"**Verdict:** {verdict}")
                            
                        with col_info:
                            st.markdown(f"**🎓 Education:** {row['Education']}")
                            st.markdown(f"**💼 Background:** {row['Experience']}")
                            
                            skills_html = "".join([f"<span class='badge'>{skill}</span>" for skill in row['Skills']])
                            st.markdown(f"**🛠️ Verified Tech Stack:**<br>{skills_html}", unsafe_allow_html=True)
                            
                            st.info(f"💡 **AI Recruiter Deep Evaluation:** {row['Reasoning']}")
                        
                        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<p class="section-title">💬 Autonomous AI HR Assistant</p>', unsafe_allow_html=True)
    st.markdown("<p style='color: #cbd5e1 !important;'>Need help drafting optimized job descriptions, generating technical interview questions, or reviewing compliance policies?</p>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am your Autonomous HR Assistant. How can I assist your engineering hiring pipeline today?"}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your question here..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ]
                )
                reply = response.choices[0].message.content
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"API Error: Make sure your .env file has a valid GROQ_API_KEY. Error: {str(e)}")