import json
import frappe
from frappe.model.document import Document
from frappe.utils.csvutils import to_csv
from frappe.utils.file_manager import save_file

class AlphaXMISImportWizard(Document):
    pass

@frappe.whitelist()
def validate_and_preview(wizard_name: str):
    wiz = frappe.get_doc("AlphaX MIS Import Wizard", wizard_name)
    mapping = _parse_json(wiz.mapping_json)

    warnings, errors = [], []
    if not wiz.excel_file:
        errors.append("excel_file is required")
    if not mapping:
        errors.append("mapping_json is required (no defaults assumed)")

    return _save_log(wiz, warnings, errors)

def _parse_json(txt):
    if not txt:
        return {}
    try:
        obj = json.loads(txt)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}

def _save_log(wiz, warnings, errors):
    rows = [{"type":"WARNING","message":w} for w in warnings] + [{"type":"ERROR","message":e} for e in errors]
    csv = to_csv(rows) if rows else "type,message\n"
    f = save_file("alphax_mis_import_log.csv", csv, wiz.doctype, wiz.name, is_private=1)
    wiz.db_set("last_log_file", f.file_url)
    wiz.db_set("last_summary", f"Warnings: {len(warnings)} | Errors: {len(errors)}")
    return {"warnings": warnings, "errors": errors, "log_file": f.file_url}
