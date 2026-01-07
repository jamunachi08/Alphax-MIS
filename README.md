# AlphaX MIS (Frappe/ERPNext v15/v16)

A **dimension-aware** MIS / BI format builder designed to replicate Excel-like MIS statements.

## No pre-defined dimension names
- User selects dimensions from ERPNext **Accounting Dimension** (dropdown/link).
- Works for LOB today, Region tomorrow, Channel next year — without renaming in code.

## Features (v0.1.0)
- Format Builder (Lines: Group / Flag / Formula)
- Flags → Accounts mapping with Dimension Scope (All / Only Selected / Exclude Selected)
- Import Wizard scaffold (setup-first; no defaults)
- Script Report: **AlphaX MIS Report**
- Page: **AlphaX MIS AI Insights** (local intelligence; optional external AI later)

## Install
```bash
bench get-app https://github.com/<your_org>/alphax_mis
bench --site <site> install-app alphax_mis
bench --site <site> migrate
```
