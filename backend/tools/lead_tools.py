import os
import re
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
# SERPER SEARCH
# =================================================
def serper_search(query: str, num_results: int = 5):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"q": query, "num": num_results}

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

# =================================================
# BUILD CONTEXT
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

# =================================================
# LEAD SUMMARY (PERSON PROFILE)
# =================================================
def summarize_lead(question: str, search_results: list):
    if not search_results:
        return []

    context = build_context(search_results)

    prompt = f"""
You are given public web information about a person.

Create a concise lead profile using ONLY the information below.
- Focus on name, role, company, and background
- Use 3 to 5 bullet points
- Do NOT add private or unverified information

Data:
{context}

Question:
{question}

Respond with each point on a new line.
Do NOT number the points.
Do NOT add extra text.
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    points = [
        line.strip("-• ").strip()
        for line in raw.split("\n")
        if line.strip()
    ]

    return points

# =================================================
# PUBLIC FUNCTION
# =================================================
def get_lead_info(query: str):
    """
    query can be:
    - email (john@abc.com)
    - name (Sundar Pichai)
    """

    # Improve search query
    if "@" in query:
        search_query = f"{query} professional profile"
    else:
        search_query = f"{query} profile CEO founder"

    results = serper_search(search_query)
    summary_points = summarize_lead(query, results)

    return {
        "summary": summary_points,
        "sources": [r["link"] for r in results]
    }
