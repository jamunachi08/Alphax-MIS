import frappe
from frappe import _
from frappe.utils import flt
from frappe.utils.csvutils import to_csv
from frappe.utils.file_manager import save_file
from alphax_mis.alphax_mis.utils.dimensions import parse_json, get_dimension_meta, gl_has_field

def execute(filters=None):
    filters = frappe._dict(filters or {})
    cols = [
        {"label": _("Line Code"), "fieldname": "line_code", "fieldtype": "Data", "width": 120},
        {"label": _("Title"), "fieldname": "title", "fieldtype": "Data", "width": 320},
        {"label": _("Amount"), "fieldname": "amount", "fieldtype": "Currency", "width": 150},
    ]
    data, warnings, errors = build_report(filters)

    if filters.get("export_log") and (warnings or errors):
        _export_log(filters, warnings, errors)

    return cols, data

def build_report(filters):
    warnings, errors = [], []
    if not filters.get("report_format"):
        return [], warnings, ["Missing report_format"]

    fmt = frappe.get_doc("AX MIS Report Format", filters.get("report_format"))

    report_dims = {}
    if filters.get("dimension") and filters.get("dimension_value"):
        fieldname, _doctype = get_dimension_meta(filters.get("dimension"))
        if fieldname and gl_has_field(fieldname):
            report_dims[fieldname] = filters.get("dimension_value")
        else:
            warnings.append("Selected dimension field not found in GL Entry; ignored.")

    extra = parse_json(filters.get("extra_dimensions_json"))
    for k, v in (extra or {}).items():
        if v in (None, ""): 
            continue
        if gl_has_field(k):
            report_dims[k] = v
        else:
            warnings.append(f"Extra dimension '{k}' not found in GL Entry; ignored.")

    cache = {}
    out = []
    for ln in (fmt.get("lines") or []):
        lc = ln.get("line_code") or ""
        title = ln.get("title") or ""
        ltype = (ln.get("line_type") or "").lower()
        amt = 0.0

        if ltype == "group":
            amt = 0.0
        elif ltype == "flag":
            if not ln.get("flag"):
                errors.append(f"Line '{lc}' is Flag but no flag selected.")
                amt = 0.0
            else:
                amt = sum_for_flag(ln.get("flag"), filters, report_dims, warnings)
        elif ltype == "formula":
            expr = (ln.get("formula") or "").strip()
            try:
                scope = {k: flt(v) for k, v in cache.items()}
                amt = flt(eval(expr, {"__builtins__": {}}, scope)) if expr else 0.0
            except Exception as e:
                errors.append(f"Formula error at '{lc}': {e}")
                amt = 0.0

        cache[lc] = amt
        out.append({"line_code": lc, "title": ("  " * int(ln.get("indent") or 0)) + title, "amount": amt})

    return out, warnings, errors

def sum_for_flag(flag_name, filters, report_dims, warnings):
    flag = frappe.get_doc("AX MIS Flag", flag_name)
    total = 0.0

    for row in (flag.get("accounts") or []):
        if not row.get("include"):
            continue
        acc = row.get("account")
        if not acc:
            continue
        weight = flt(row.get("weight") or 1)
        dims = dict(report_dims)

        scope = (row.get("dimension_scope") or "All").strip()
        df = row.get("dimension_filters") or []

        pairs = []
        for f in df:
            dim = f.get("dimension")
            val = f.get("value")
            if not dim or not val:
                continue
            fieldname, _doctype = get_dimension_meta(dim)
            if not fieldname:
                continue
            if not gl_has_field(fieldname):
                warnings.append(f"Account '{acc}': field '{fieldname}' missing in GL Entry; ignored.")
                continue
            pairs.append((fieldname, val))

        if scope == "All" or not pairs:
            total += weight * sum_gl(acc, filters, dims)
        elif scope == "Only Selected":
            s = 0.0
            for fieldname, val in pairs:
                d2 = dict(dims); d2[fieldname] = val
                s += sum_gl(acc, filters, d2)
            total += weight * s
        elif scope == "Exclude Selected":
            base = sum_gl(acc, filters, dims)
            sub = 0.0
            for fieldname, val in pairs:
                d2 = dict(dims); d2[fieldname] = val
                sub += sum_gl(acc, filters, d2)
            total += weight * (base - sub)
        else:
            total += weight * sum_gl(acc, filters, dims)

    return total

def sum_gl(account, filters, dims):
    cond = ["account=%(account)s", "posting_date between %(from_date)s and %(to_date)s", "is_cancelled=0"]
    params = {"account": account, "from_date": filters.get("from_date"), "to_date": filters.get("to_date")}
    if filters.get("company"):
        cond.append("company=%(company)s")
        params["company"] = filters.get("company")
    for k, v in (dims or {}).items():
        if v in (None, ""): 
            continue
        if gl_has_field(k):
            cond.append(f"`{k}`=%({k})s")
            params[k] = v

    sql = f"select ifnull(sum(debit),0)-ifnull(sum(credit),0) from `tabGL Entry` where {' and '.join(cond)}"
    return frappe.db.sql(sql, params)[0][0] or 0.0

def _export_log(filters, warnings, errors):
    rows = [{"type":"WARNING","message":w} for w in warnings] + [{"type":"ERROR","message":e} for e in errors]
    csv = to_csv(rows) if rows else "type,message\n"
    fmt = filters.get("report_format") or "unknown"
    save_file(f"alphax_mis_log_{fmt}.csv", csv, "AX MIS Report Format", fmt, is_private=1)
