import frappe
from frappe.utils import flt
from alphax_mis.alphax_mis.report.alphax_mis_report.alphax_mis_report import build_report

@frappe.whitelist()
def run_insights(report_format=None, from_date=None, to_date=None, company=None):
    data, warnings, errors = build_report(frappe._dict({
        "report_format": report_format,
        "from_date": from_date,
        "to_date": to_date,
        "company": company,
    }))

    insights = []
    if errors:
        insights.append("❗ Errors found. Fix format/flag mappings first.")
    if warnings:
        insights.append("⚠️ Warnings found. Some dimension fields may be missing in GL Entry.")

    nums = [(d.get("title"), flt(d.get("amount"))) for d in data if flt(d.get("amount")) != 0]
    nums_sorted = sorted(nums, key=lambda x: abs(x[1]), reverse=True)
    for t, a in nums_sorted[:5]:
        insights.append(f"Top line: {t} = {a:,.2f}")

    return {"insights": insights}
