"""LLM provider. To switch provider, rewrite generate_json() keeping the same signature."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


def generate_json(prompt: str) -> str:
    """Send the prompt to Gemini and return the raw text of the answer (expected to be JSON)."""
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest"),
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return response.text
