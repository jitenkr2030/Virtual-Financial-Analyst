# Virtual Financial Analyst (VFA) — Django starter

A runnable Django financial intelligence workspace covering the 15-module product architecture with working foundational workflows.

## Included
- Organization and financial-period workspaces
- Manual financial entry and CSV/XLSX import
- Financial statement aggregation and ratio analysis
- Rule-based indicative financial health score
- Forecast scenarios and simplified three-year income statement projection
- DCF valuation, NPV, ROI, break-even, margin, CAGR and cash runway calculators
- Budget lines, variance view, working-capital and cash-flow proxies
- Segment/customer profitability, KPI trends and threshold-based risk alerts
- Built-in explainable financial assistant (no external AI key required)
- Research notes, saved reports, CSV/XLSX/PDF exports
- Client workspace, document upload and audit trail
- Django admin and authentication

## Quick start (Linux / WSL / macOS)
```bash
cd vfa_django
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000 and sign in with the superuser you created.

## Windows PowerShell
```powershell
cd vfa_django
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## First-use sequence
1. Sign in.
2. Create an organization from the dashboard.
3. Create a financial period at **Periods**.
4. Add records at **Financial statements**, or download the sample CSV and import it.
5. Review ratios, cash flow, profitability, risk signals and KPIs.
6. Create a scenario under Financial models; run DCF under Valuation.
7. Generate a report and export PDF, XLSX or CSV.

## Import format
CSV/XLSX requires these columns:
`category`, `label`, `amount`
Optional columns: `department`, `segment`, `customer`.

Supported categories:
`revenue, cogs, opex, other_income, interest, tax, cash, receivables, inventory, current_assets, fixed_assets, payables, short_debt, long_debt, equity, depreciation, capex`.

Use positive values for each line item. Do not enter negative expenses unless your accounting convention specifically requires it.

## Production hardening required before real client / financial use
This is a functional starter, not certified accounting, audit, tax, investment or valuation software. Before production:
- Configure PostgreSQL, HTTPS, secure SECRET_KEY, DEBUG=False, ALLOWED_HOSTS and secure cookie settings.
- Add organization-level object permissions and role-based access control; current starter is a trusted single-workspace prototype and does not provide tenant isolation.
- Add backups, retention, malware scanning and private media storage.
- Add review/approval states, immutable audit controls and data-import reconciliation.
- Validate accounting mappings, opening/closing balances and the balance-sheet equation.
- Have qualified finance professionals review formulas, assumptions and generated outputs.
- AI assistant is rule-based only. Connect an approved LLM provider with privacy controls if AI-generated narratives are required.
- Forecasting is a simplified operating forecast, not a fully integrated three-statement model.
- Cash flow and risk indicators are proxies and should not be treated as formal financial advice.

## Notes
- The app uses SQLite by default for easy local setup.
- The app has no demo login/password. Create your own administrator.
- Native Excel export/import requires `pandas` and `openpyxl`, installed through requirements.
