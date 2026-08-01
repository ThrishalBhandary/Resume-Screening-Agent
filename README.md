# 🚀 AI Resume Screener & HR Suite

<p align="center">
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Groq-Llama%203.1-8B?style=for-the-badge&logo=groq&logoColor=white" alt="Groq Llama 3.1" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
</p>

> An intelligent, high-precision resume screening and candidate ranking web application powered by Streamlit, Groq, and NLP.

## ✨ Overview

This project helps recruiters and hiring teams automate resume analysis by:

- parsing candidate resumes and job descriptions,
- comparing qualification fit using AI reasoning,
- ranking applicants on a clear leaderboard,
- and supporting HR-oriented conversational assistance through a built-in assistant.

## 🌟 Key Features

- 📄 AI Resume Intelligence Dashboard
  - Upload multiple resumes and a job description
  - Generate instant ranking and structured candidate insights

- 🎯 Semantic Candidate Scoring
  - Go beyond keyword matching
  - Evaluate experience, technical alignment, and role suitability intelligently

- 💬 AI HR Assistant
  - Draft job descriptions, create interview questions, and help with recruiter workflows

- 🎨 Modern SaaS UI
  - Clean dashboard, glassmorphism visuals, progress bars, and precision badges

- ⚙️ Workspace Control Center
  - Monitor system state
  - View project metadata
  - Reset the workspace with one click

## 🛠️ Tech Stack

| Area | Tool |
|---|---|
| Frontend | Streamlit |
| AI Model | Groq API (`llama-3.1-8b-instant`) |
| PDF Parsing | PyPDF2 |
| Data Processing | Pandas |
| Environment Setup | python-dotenv |

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install streamlit PyPDF2 pandas groq scikit-learn python-dotenv
```

### 2. Add Your Groq API Key

Create a `.env` file in the project root and add:

```bash
GROQ_API_KEY=gsk_your_actual_key_here
```

### 3. Launch the App

```bash
streamlit run agent.py
```

Then open the local URL shown in your terminal, usually:

```text
http://localhost:8501
```

## 📌 Developer

- Developer: Thrishal
- Version: 1.0.0
- Core Model: Llama 3.1 via Groq

## 🧾 Project Purpose

This application is designed for fast, scalable, and intelligent recruitment screening with a modern AI-first workflow for HR teams.

