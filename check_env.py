from dotenv import load_dotenv
import os

load_dotenv()

keys = [
    "AZURE_OPENAI_ENDPOINT",
    "OPENAI_API_KEY",
    "OPENAI_API_VERSION",
    "OPENAI_MODEL_NAME",
    "SERPER_API_KEY",
]

for k in keys:
    v = os.getenv(k)
    print(f"{k}: {'SET' if v else 'MISSING'} (len={len(v) if v else 0})")
