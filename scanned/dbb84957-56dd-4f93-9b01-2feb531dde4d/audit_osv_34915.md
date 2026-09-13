# [M] CVE-2025-66436

## Summary
Severity: Medium
Advisory: CVE-2025-66436
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-66436
Type: osv

## Details
An SSTI (Server-Side Template Injection) vulnerability exists in the get_terms_and_conditions method of Frappe ERPNext through 15.89.0. The function renders attacker-controlled Jinja2 templates (terms) using frappe.render_template() with a user-supplied context (doc). Although Frappe uses a custom SandboxedEnvironment, several dangerous globals such as frappe.db.sql are still available in the execution context via get_safe_globals(). An authenticated attacker with access to create or modify a Terms and Conditions document can inject arbitrary Jinja expressions into the terms field, resulting in server-side code execution within a restricted but still unsafe context. This vulnerability can be used to leak database information.

## References
- https://iamanc.github.io/post/erpnext-ssti-bug-3
- https://www.notion.so/SSTI-bug-3-239e6086eadc8020aeecdaf123e32f3d?source=copy_link
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66436.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66436
