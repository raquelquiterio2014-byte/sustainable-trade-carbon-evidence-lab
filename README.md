# Sustainable Trade & Carbon Evidence Lab V1.0

**COP31 AI Solutions Lab · Day 5 · November 13, 2026**

Independent educational Streamlit application exploring Brazil–EU trade, illustrative emissions, regulatory source traceability, Gemini-assisted evidence extraction, and human oversight.

## Important status
- Application source and synthetic sample data included.
- Live Gemini API request **not yet verified**; requires the user's API key and a live test.
- UI screenshots and real-world carbon validations **not yet verified**.
- Not a legal compliance, certified emissions, or customs calculation tool.

## Windows and PyCharm setup
1. Use Python 3.12 and create a virtual environment.
2. Run `python -m pip install -r requirements.txt`.
3. Run `python -m pytest -q`.
4. Run `python -m streamlit run app.py`.
5. For optional live Gemini calls, copy `.env.example` to `.env` and supply `GEMINI_API_KEY`. Never commit your `.env`.

## Five modules
1. Trade & Carbon Overview
2. Carbon Calculations
3. Regulatory Evidence
4. AI Evidence Analyst (optional external API call)
5. Human Review & Audit

## Caveats
All bundled sample emissions factors are synthetic educational assumptions. The simplified calculation is not CBAM embedded-emissions accounting or a lifecycle assessment. AI-extracted claims need external source confirmation and human review. Do not paste confidential information into an external API.

**Evidence first. Engineering second. Measurable impact as the goal.**
