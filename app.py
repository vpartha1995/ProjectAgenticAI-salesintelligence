from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# =================================================
# LOAD ENV VARIABLES
# =================================================
load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not all([
    AZURE_OPENAI_ENDPOINT,
    OPENAI_API_KEY,
    OPENAI_API_VERSION,
    OPENAI_MODEL_NAME,
    SERPER_API_KEY
]):
    raise ValueError("❌ Missing environment variables")

# =================================================
# INITIALIZE FLASK APP
# =================================================
app = Flask(__name__, static_folder='static')
CORS(app)

# =================================================
# AZURE OPENAI LLM
# =================================================
llm = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version=OPENAI_API_VERSION,
    deployment_name=OPENAI_MODEL_NAME,
    temperature=0
)

# =================================================
# SERPER SEARCH FUNCTIONS
# =================================================
def serper_search(query: str, num_results: int = 5):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"q": query, "num": num_results}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code != 200:
            return []

        data = response.json()
        results = []

        for item in data.get("organic", []):
            results.append({
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link")
            })

        return results
    except Exception as e:
        print(f"Search error: {e}")
        return []

def serper_news_search(query: str, num_results: int = 5):
    url = "https://google.serper.dev/news"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"q": query, "num": num_results}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code != 200:
            return []

        data = response.json()
        results = []

        for item in data.get("news", []):
            results.append({
                "title": item.get("title"),
                "snippet": item.get("snippet"),
                "link": item.get("link"),
                "date": item.get("date")
            })

        return results
    except Exception as e:
        print(f"News search error: {e}")
        return []

# =================================================
# HELPER FUNCTIONS
# =================================================
def build_context(results):
    context = ""
    for idx, r in enumerate(results, 1):
        context += f"""
SOURCE {idx}:
Title: {r['title']}
Snippet: {r['snippet']}
URL: {r['link']}
"""
    return context.strip()

def build_news_context(results):
    context = ""
    for idx, r in enumerate(results, 1):
        context += f"""
NEWS {idx}:
Title: {r['title']}
Snippet: {r['snippet']}
Date: {r['date']}
URL: {r['link']}
"""
    return context.strip()

# =================================================
# COMPANY RESEARCH
# =================================================
def get_company_details(question: str):
    search_results = serper_search(question)
    
    if not search_results:
        return {"summary": ["No information found"], "sources": []}

    context = build_context(search_results)

    prompt = f"""
You are given web search results about a company.

Create a concise summary using ONLY the information below.
- Focus on key facts about the company
- Use 3 to 5 bullet points
- Each point should be factual and concise

Search Results:
{context}

Question: {question}

Respond with each point on a new line.
Do NOT number the points.
"""

    try:
        response = llm.invoke(prompt)
        raw = response.content.strip()
        
        points = [
            line.strip("-• ").strip()
            for line in raw.split("\n")
            if line.strip() and not line.strip().startswith("Question:")
        ]
        
        return {
            "summary": points[:5] if points else ["No summary available"],
            "sources": [r["link"] for r in search_results]
        }
    except Exception as e:
        print(f"LLM error: {e}")
        return {
            "summary": ["Error generating summary"],
            "sources": [r["link"] for r in search_results]
        }

# =================================================
# NEWS RESEARCH
# =================================================
def get_tech_news(question: str):
    news_results = serper_news_search(question)
    
    if not news_results:
        return {"summary": ["No news found"], "sources": []}

    context = build_news_context(news_results)

    prompt = f"""
You are given recent news articles.

Summarize the key trends and developments using ONLY the information below.
- Focus on trends and recent updates
- Use 3 to 5 bullet points
- Each point should be factual and concise

News Data:
{context}

Question: {question}

Respond with each point on a new line.
Do NOT number the points.
"""

    try:
        response = llm.invoke(prompt)
        raw = response.content.strip()
        
        points = [
            line.strip("-• ").strip()
            for line in raw.split("\n")
            if line.strip() and not line.strip().startswith("Question:")
        ]
        
        return {
            "summary": points[:5] if points else ["No summary available"],
            "sources": [n["link"] for n in news_results]
        }
    except Exception as e:
        print(f"LLM error: {e}")
        return {
            "summary": ["Error generating summary"],
            "sources": [n["link"] for n in news_results]
        }

# =================================================
# LEAD RESEARCH
# =================================================
def get_lead_info(query: str):
    if "@" in query:
        search_query = f"{query} professional profile"
    else:
        search_query = f"{query} profile CEO founder"

    results = serper_search(search_query)
    
    if not results:
        return {"summary": ["No information found"], "sources": []}

    context = build_context(results)

    prompt = f"""
You are given public web information about a person.

Create a concise lead profile using ONLY the information below.
- Focus on name, role, company, and background
- Use 3 to 5 bullet points
- Do NOT add private or unverified information

Data:
{context}

Question: {query}

Respond with each point on a new line.
Do NOT number the points.
"""

    try:
        response = llm.invoke(prompt)
        raw = response.content.strip()
        
        points = [
            line.strip("-• ").strip()
            for line in raw.split("\n")
            if line.strip() and not line.strip().startswith("Question:")
        ]
        
        return {
            "summary": points[:5] if points else ["No summary available"],
            "sources": [r["link"] for r in results]
        }
    except Exception as e:
        print(f"LLM error: {e}")
        return {
            "summary": ["Error generating summary"],
            "sources": [r["link"] for r in results]
        }

# =================================================
# FLASK ROUTES
# =================================================
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/company', methods=['POST'])
def company_endpoint():
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        result = get_company_details(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/news', methods=['POST'])
def news_endpoint():
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        result = get_tech_news(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lead', methods=['POST'])
def lead_endpoint():
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        result = get_lead_info(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"})

# =================================================
# RUN SERVER
# =================================================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)