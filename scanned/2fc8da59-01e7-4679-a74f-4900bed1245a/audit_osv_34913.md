# [H] CVE-2025-66434

## Summary
Severity: High
Advisory: CVE-2025-66434
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-66434
Type: osv

## Details
An SSTI (Server-Side Template Injection) vulnerability exists in the get_dunning_letter_text method of Frappe ERPNext through 15.89.0. The function renders attacker-controlled Jinja2 templates (body_text) using frappe.render_template() with a user-supplied context (doc). Although Frappe uses a custom SandboxedEnvironment, several dangerous globals such as frappe.db.sql are still available in the execution context via get_safe_globals(). An authenticated attacker with access to configure Dunning Type and its child table Dunning Letter Text can inject arbitrary Jinja expressions, resulting in server-side code execution within a restricted but still unsafe context. This can leak database information.

## References
- https://iamanc.github.io/post/erpnext-ssti-bug-1
- https://www.notion.so/SSTI-bug-1-239e6086eadc8096bfcfe90551a3a483?source=copy_link
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66434.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66434
