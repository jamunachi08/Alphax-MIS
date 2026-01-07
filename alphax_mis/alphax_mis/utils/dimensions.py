import json
import frappe

def parse_json(txt):
    if not txt:
        return {}
    try:
        obj = json.loads(txt)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}

def gl_has_field(fieldname: str) -> bool:
    try:
        return frappe.db.has_column("GL Entry", fieldname)
    except Exception:
        return False

def get_dimension_meta(accounting_dimension_name: str):
    dim = frappe.get_doc("Accounting Dimension", accounting_dimension_name)
    return dim.get("fieldname"), dim.get("document_type")
