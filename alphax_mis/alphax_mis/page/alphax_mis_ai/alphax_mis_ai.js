frappe.pages['alphax-mis-ai'].on_page_load = function(wrapper) {
  const page = frappe.ui.make_app_page({ parent: wrapper, title: __('AlphaX MIS AI Insights'), single_column: true });
  const $body = $(page.body).append('<div class="p-3"></div>');
  $body.append(`
    <div class="card">
      <div class="card-body">
        <p class="mb-2"><b>Local Intelligence</b>: highlights top lines and basic signals from AlphaX MIS Report output.</p>
        <button class="btn btn-primary" id="run">Run Insights</button>
        <div class="mt-3" id="out"></div>
      </div>
    </div>
  `);

  $body.on('click', '#run', async () => {
    const v = await frappe.prompt([
      {fieldname:'report_format', label:'Report Format', fieldtype:'Link', options:'AX MIS Report Format', reqd:1},
      {fieldname:'from_date', label:'From Date', fieldtype:'Date', reqd:1},
      {fieldname:'to_date', label:'To Date', fieldtype:'Date', reqd:1},
      {fieldname:'company', label:'Company', fieldtype:'Link', options:'Company'}
    ], __('Run Insights'));

    frappe.call({
      method: 'alphax_mis.alphax_mis.page.alphax_mis_ai.alphax_mis_ai.run_insights',
      args: v,
      callback: (r) => {
        const m = r.message || {};
        const items = (m.insights || []).map(x => `<li>${frappe.utils.escape_html(x)}</li>`).join('');
        $('#out').html(`<ul>${items || '<li>No insights</li>'}</ul>`);
      }
    });
  });
};
