frappe.query_reports["AlphaX MIS Report"] = {
  "filters": [
    {"fieldname":"company","label":"Company","fieldtype":"Link","options":"Company"},
    {"fieldname":"report_format","label":"Report Format","fieldtype":"Link","options":"AX MIS Report Format","reqd":1},
    {"fieldname":"from_date","label":"From Date","fieldtype":"Date","reqd":1},
    {"fieldname":"to_date","label":"To Date","fieldtype":"Date","reqd":1},

    {"fieldname":"dimension","label":"Dimension (Any)","fieldtype":"Link","options":"Accounting Dimension"},
    {"fieldname":"dimension_value_doctype","label":"Dimension Doctype","fieldtype":"Data","read_only":1},
    {"fieldname":"dimension_value","label":"Dimension Value","fieldtype":"Dynamic Link","options":"dimension_value_doctype"},

    {"fieldname":"extra_dimensions_json","label":"Extra Dimensions (JSON)","fieldtype":"Code","options":"JSON"},
    {"fieldname":"export_log","label":"Export warnings/errors as CSV attachment","fieldtype":"Check"}
  ],
  "onload": function(report) {
    const set_doctype = () => {
      const dim = report.get_values().dimension;
      if (!dim) return report.set_filter_value('dimension_value_doctype', '');
      frappe.db.get_value('Accounting Dimension', dim, ['document_type'], (r) => {
        report.set_filter_value('dimension_value_doctype', (r && r.document_type) ? r.document_type : '');
      });
    };
    report.page.fields_dict.dimension.df.onchange = set_doctype;
  }
};
