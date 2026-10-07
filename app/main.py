import logging

from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from app import llm
from app.schemas import ExtractionResult, ExtractRequest

logger = logging.getLogger(__name__)

app = FastAPI(title="Extractor API")

MAX_ATTEMPTS = 2

PROMPT = """Extract information from the text below. Answer ONLY with a JSON object with these keys:
- "title": short title (string)
- "category": category of the product or job offer (string)
- "provider": company or provider name, or null if not mentioned
- "price": price exactly as written, including currency, or null if not mentioned
- "summary": one-sentence summary (string)

Text:
{text}
"""


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract")
def extract(request: ExtractRequest) -> ExtractionResult:
    prompt = PROMPT.format(text=request.text)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            raw = llm.generate_json(prompt)
        except Exception:
            logger.exception("LLM call failed")
            raise HTTPException(status_code=503, detail="LLM service unavailable.")

        try:
            return ExtractionResult.model_validate_json(raw)
        except ValidationError as error:
            logger.warning("Attempt %d: invalid LLM response: %s", attempt, error)

    raise HTTPException(status_code=502, detail="The LLM returned an invalid response.")
