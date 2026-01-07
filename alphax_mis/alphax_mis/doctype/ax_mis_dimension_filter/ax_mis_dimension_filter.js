frappe.ui.form.on('AX MIS Dimension Filter', {
  dimension: function(frm, cdt, cdn) {
    const row = locals[cdt][cdn];
    if (!row.dimension) return;
    frappe.db.get_value('Accounting Dimension', row.dimension, ['document_type'], (r) => {
      if (r && r.document_type) {
        row.dimension_doctype = r.document_type;
        frm.refresh_field('dimension_filters');
      }
    });
  }
});
