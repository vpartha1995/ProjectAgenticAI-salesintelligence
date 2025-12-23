🚀 Sales Intelligence Agent

A Sales Intelligence Agent that provides company insights, technology/news trends, and lead (person) profiles using real-time web data and LLM-powered summarization.

Built for hackathons and demos with a clear separation of tools and a simple web interface.

🔧 Tech Stack Backend

Python

Flask

Azure OpenAI

Serper API (Google Search & News)

LangChain

Frontend

HTML

CSS

JavaScript

✨ Features 🏢 Company Intelligence

Company overview & background

Key information summarized into bullet points

Transparent source links

📰 News & Technology Trends

Recent technology trends

Latest company and industry news

Time-sensitive summaries from live web data

👤 Lead Intelligence

Public professional profiles

Role, company, and background

Ethical, public data only (no private scraping)

🧠 System Architecture User Input ↓ Tool Selection (Company / News / Lead) ↓ Serper Search (Web / News) ↓ LLM Summarization (Azure OpenAI) ↓ Summary Points + Source Links

Each tool is optimized for a specific entity type:

Company → Organizations

News → Events & trends

Lead → Individuals

🖥️ Web Interface

Single-page web app

Dropdown to select:

Company

News

Lead

Input box for query

Displays:

Bullet-point summaries

Clickable source links

📁 Project Structure
Sales_agent/
│
├── backend/
│   ├── companytools.py
│   ├── newstools.py
│   ├── leadtools.py
│   └── app.py        # Flask backend
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
