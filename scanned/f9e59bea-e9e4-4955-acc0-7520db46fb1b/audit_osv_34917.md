# [C] CVE-2025-66438

## Summary
Severity: Critical
Advisory: CVE-2025-66438
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-66438
Type: osv

## Details
A Server-Side Template Injection (SSTI) vulnerability exists in the Frappe ERPNext through 15.89.0 Print Format rendering mechanism. Specifically, the API frappe.www.printview.get_html_and_style() triggers the rendering of the html field inside a Print Format document using frappe.render_template(template, doc) via the get_rendered_template() call chain. Although ERPNext wraps Jinja2 in a SandboxedEnvironment, it exposes sensitive functions such as frappe.db.sql through get_safe_globals(). An authenticated attacker with permission to create or modify a Print Format can inject arbitrary Jinja expressions into the html field. Once the malicious Print Format is saved, the attacker can call get_html_and_style() with a target document (e.g., Supplier or Sales Invoice) to trigger the render process. This leads to information disclosure from the database, such as database version, schema details, or sensitive values, depending on the injected payload. Exploitation flow: Create a Print Format with SSTI payload in the html field; call the get_html_and_style() API; triggers frappe.render_template(template, doc) inside get_rendered_template(); leaks database information via frappe.db.sql or other exposed globals.

## References
- https://iamanc.github.io/post/erpnext-ssti-bug-5
- https://www.notion.so/SSTI-bug-5-239e6086eadc80a48f17c1257a604d2c?source=copy_link
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66438.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66438
