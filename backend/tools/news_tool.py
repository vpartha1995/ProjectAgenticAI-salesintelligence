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
# AZURE OPENAI LLM (REASONING ONLY)
# =================================================
llm = AzureChatOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version=OPENAI_API_VERSION,
    deployment_name=OPENAI_MODEL_NAME,
    temperature=0
)

# =================================================
# SERPER NEWS SEARCH TOOL
# =================================================
def serper_news_search(query: str, num_results: int = 5):
    url = "https://google.serper.dev/news"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "q": query,
        "num": num_results
    }

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

# =================================================
# BUILD CONTEXT FROM NEWS RESULTS
# =================================================
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
# LLM NEWS SUMMARY (TRENDS / TECHNOLOGY)
# =================================================
def summarize_news(question: str, news_results: list):
    if not news_results:
        return []

    context = build_news_context(news_results)

    prompt = f"""
You are given recent technology news articles.

Summarize the key trends and recent developments using ONLY the information below.
- Focus on trends, new technology, and recent updates
- No opinions
- No future predictions
- 3 to 5 points

News Data:
{context}

Question:
{question}

Respond with each point on a new line.
Do NOT number the points.
Do NOT add extra text.
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    # Safe parsing
    points = [
        line.strip("-• ").strip()
        for line in raw.split("\n")
        if line.strip()
    ]

    return points

# =================================================
# PUBLIC FUNCTION (IMPORT THIS)
# =================================================
def get_tech_news(question: str):
    news_results = serper_news_search(question)
    summary_points = summarize_news(question, news_results)

    return {
        "summary": summary_points,
        "sources": [n["link"] for n in news_results]
    }
