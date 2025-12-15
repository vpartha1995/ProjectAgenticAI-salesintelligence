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
# SERPER SEARCH TOOL
# =================================================
def serper_search(query: str, num_results: int = 5):
    url = "https://google.serper.dev/search"
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

    for item in data.get("organic", []):
        results.append({
            "title": item.get("title"),
            "snippet": item.get("snippet"),
            "link": item.get("link")
        })

    return results

# =================================================
# BUILD CONTEXT FROM SEARCH RESULTS
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
# LLM ANSWER MODULE (STRICT)
# =================================================
def answer_from_search(question: str, search_results: list):
    if not search_results:
        return []

    context = build_context(search_results)

    prompt = f"""
You are given web search results retrieved from the internet.

Create a concise summary in bullet points using ONLY the information below.
- Each bullet must be a factual statement.
- Do NOT add new information.
- Return 3 to 5 bullet points.
- If information is insufficient, return an empty list.

Search Results:
{context}

Question:
{question}

Respond ONLY as a Python-style list of strings.
Example:
["Point 1", "Point 2"]
"""

    response = llm.invoke(prompt)
    raw = response.content.strip()

    try:
        summary_points = eval(raw)
        if isinstance(summary_points, list):
            return summary_points
    except:
        pass

    return []

# =================================================
# PUBLIC FUNCTION (IMPORT THIS)
# =================================================
def get_company_details(question: str):
    search_results = serper_search(question)
    summary_points = answer_from_search(question, search_results)

    return {
        "summary": summary_points,
        "sources": [r["link"] for r in search_results]
    }

