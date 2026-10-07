# Structured Data Extractor

[![CI](https://github.com/joseebelloo/structured-data-extractor/actions/workflows/ci.yml/badge.svg)](https://github.com/joseebelloo/structured-data-extractor/actions/workflows/ci.yml)

**English** | [Español](#español)

REST API that turns unstructured text (a product description, a job offer...) into structured JSON using Google Gemini.

- **FastAPI** with Pydantic models to validate requests and the LLM output.
- If the LLM returns malformed JSON or missing fields, it retries once and then returns a controlled `502` error.
- The LLM call lives in its own module (`app/llm.py`), so the provider can be swapped easily.
- **pytest** tests with the LLM mocked: they run without an API key.
- **GitHub Actions** runs ruff, pytest and the Docker build on every push and pull request.

## Run locally

Get a free API key at [Google AI Studio](https://aistudio.google.com), then:

```bash
cp .env.example .env          # add your GEMINI_API_KEY
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Interactive docs: http://localhost:8000/docs

### With Docker

```bash
docker build -t extractor-api .
docker run --rm --env-file .env -p 8000:8000 extractor-api
```

## Run the tests

```bash
pytest -v
ruff check .
```

## Example

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "We are hiring a Junior Data Engineer in Madrid at Stratebi. Python, SQL and Airflow. Salary 28,000-32,000 € gross/year."}'
```

```json
{
  "title": "Junior Data Engineer",
  "category": "Job Offer",
  "provider": "Stratebi",
  "price": "28,000-32,000 € gross/year",
  "summary": "Stratebi is hiring a Junior Data Engineer in Madrid with experience in Python, SQL, and Airflow for a salary of 28,000-32,000 € gross/year."
}
```

| Endpoint | Description |
|---|---|
| `GET /health` | Health check: `{"status": "ok"}` |
| `POST /extract` | `200` result · `422` invalid input · `502` invalid LLM response · `503` LLM unavailable |

---

## Español

API REST que convierte texto no estructurado (la descripción de un producto, una oferta de empleo...) en JSON estructurado usando Google Gemini.

- **FastAPI** con modelos Pydantic para validar las peticiones y la salida del LLM.
- Si el LLM devuelve un JSON mal formado o con campos ausentes, reintenta una vez y después devuelve un error controlado `502`.
- La llamada al LLM está en su propio módulo (`app/llm.py`), para poder cambiar de proveedor fácilmente.
- Tests con **pytest** con el LLM simulado (*mock*): se ejecutan sin clave de API.
- **GitHub Actions** ejecuta ruff, pytest y el build de Docker en cada push y pull request.

## Ejecutar en local

Consigue una clave gratuita en [Google AI Studio](https://aistudio.google.com) y después:

```bash
cp .env.example .env          # añade tu GEMINI_API_KEY
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Documentación interactiva: http://localhost:8000/docs

### Con Docker

```bash
docker build -t extractor-api .
docker run --rm --env-file .env -p 8000:8000 extractor-api
```

## Ejecutar los tests

```bash
pytest -v
ruff check .
```

## Ejemplo

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Buscamos Junior Data Engineer en Madrid para Stratebi. Python, SQL y Airflow. Salario 28.000-32.000 € brutos/año."}'
```

```json
{
  "title": "Junior Data Engineer",
  "category": "Job Offer",
  "provider": "Stratebi",
  "price": "28.000-32.000 € brutos/año",
  "summary": "Stratebi is looking for a Junior Data Engineer in Madrid with experience in Python, SQL, and Airflow, offering a gross annual salary of 28,000 to 32,000 euros."
}
```

| Endpoint | Descripción |
|---|---|
| `GET /health` | Comprobación de estado: `{"status": "ok"}` |
| `POST /extract` | `200` resultado · `422` entrada inválida · `502` respuesta del LLM no válida · `503` LLM no disponible |
