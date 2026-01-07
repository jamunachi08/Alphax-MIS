frappe.ui.form.on('AlphaX MIS Import Wizard', {
  refresh(frm) {
    frm.add_custom_button(__('Validate / Preview'), () => {
      frappe.call({
        method: 'alphax_mis.alphax_mis.doctype.alphax_mis_import_wizard.alphax_mis_import_wizard.validate_and_preview',
        args: { wizard_name: frm.doc.name },
        callback: (r) => {
          const m = r.message || {};
          frappe.msgprint({
            title: __('Import Check Result'),
            message: __('Warnings: {0}<br>Errors: {1}<br>Log: {2}', [
              (m.warnings || []).length,
              (m.errors || []).length,
              m.log_file ? `<a href="${m.log_file}" target="_blank">${m.log_file}</a>` : '-'
            ]),
            indicator: (m.errors && m.errors.length) ? 'red' : 'green'
          });
        }
      });
    });
  }
});
