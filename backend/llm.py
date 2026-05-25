import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("LLM_API_KEY")
        if not api_key:
            raise ValueError("LLM_API_KEY not set in environment.")
        _client = Groq(api_key=api_key)
    return _client

def call_llm(prompt: str) -> str:
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=512
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        error_msg = str(e).lower()
        if "api key" in error_msg or "invalid" in error_msg:
            raise ValueError("Invalid API key. Please check your LLM_API_KEY.")
        elif "quota" in error_msg or "rate" in error_msg:
            raise RuntimeError("Rate limit exceeded. Please try again later.")
        elif "timeout" in error_msg:
            raise TimeoutError("Request timed out. Please try again.")
        else:
            raise RuntimeError(f"LLM error: {str(e)}")
