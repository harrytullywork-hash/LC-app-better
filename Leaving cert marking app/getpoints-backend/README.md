# getpoints backend

A minimal Flask backend for getpoints, so your API key stays secure on the server.

## Setup

1. Open a terminal in `getpoints-backend`.
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your API key.

## Run

```powershell
python app.py
```

The backend will run at `http://127.0.0.1:5000`.

## API

POST `/api/grade`

## Cross-origin usage

This backend supports CORS for `/api/*`, so the landing page can call it from a different origin once deployed.

Body JSON:
```json
{
  "question": "Question text here",
  "answer": "Student answer here"
}
```

Response:
```json
{
  "success": true,
  "grading": "...structured grading output..."
}
```

## Notes
- This keeps your API key hidden from users.
- Use the `AI_PROVIDER` variable to switch between Anthropic and OpenAI.
