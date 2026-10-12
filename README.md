# Al-Munaqqib Engineering Suite v6

A Streamlit prototype for preliminary artificial-lift screening, simplified SRP/ESP estimates, Vogel IPR visualization, well-log/data-file inspection (LAS/CSV/Excel), optional Gemini assistance, and downloadable reports.

## Important engineering limitation
This is an educational/prototype tool, not an approved field-design system. Screening rules and cost assumptions are illustrative. SRP and ESP calculations are simplified and do not replace accepted design methods, pump/vendor curves, fluid properties, pressure-loss calculations, rod-string analysis, or qualified engineering review. The ESP horsepower output is explicitly a placeholder, not a motor-sizing recommendation. Check units and correlation applicability before using results.

## Run locally
Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a local URL, normally `http://localhost:8501`.

## Run tests
```bash
pytest -q
```
Tests cover screening validation, simplified SRP/ESP functions, Vogel IPR, CSV parsing, summary statistics, and empty-file validation. LAS and Excel parsing should also be verified against representative files from your own workflow.

## Deploy on Streamlit Community Cloud
1. Upload `app.py`, `requirements.txt`, `README.md`, and `tests/` to a GitHub repository.
2. In Streamlit Community Cloud, create an app from the repository and choose `app.py` as the main file.
3. Deploy and inspect logs if dependency installation fails.
4. Do not commit API keys. Enter the Gemini key in the app's sidebar only when using the AI tab. For a production deployment, prefer Streamlit secrets or a server-side secret manager and add rate limits/access controls.

## File analysis behavior
- CSV: delimiter inference; numeric-looking columns are converted where appropriate.
- Excel: reads the first worksheet by default.
- LAS: uses `lasio`, extracts curve data and attempts to display the well name.
- Displays preview, missing-value counts, per-column statistics, curve plots, and normalized CSV/statistics downloads.

## Known next steps before production
- Add LAS fixtures covering different encodings, wrapped data and null values.
- Add data-size limits, authentication, per-user quotas and privacy/retention controls.
- Improve engineering models using validated equations and input parameters, and compare outputs against known field/vendor cases.
- Store session results explicitly if cross-tab/session persistence beyond the current Streamlit session is required.
