# [M] Frappe Framework Development Branch Incorrect Authorization via Jinja Template Preview Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-82634
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-30
Source: https://osv.dev/vulnerability/CVE-2026-82634
Type: osv

## Details
Frappe Framework development builds contain an authorization flaw in the render_jinja_template endpoint that allows low-privileged users to render arbitrary Jinja templates by supplying raw template strings. Attackers with print permission on any document can execute arbitrary SELECT statements against unrelated tables, including reading password hashes from the __Auth table.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82634.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82634
- https://www.vulncheck.com/advisories/frappe-framework-development-branch-incorrect-authorization-via-jinja-template-preview-endpoint
- https://github.com/frappe/frappe/commit/37d2eb59790633da01c741b950cc00ca3558c494
- https://github.com/frappe/frappe/pull/40710
- https://github.com/frappe/frappe
- https://github.com/frappe/frappe/blob/0a80046da32bb8976cd7854f551c179a4a06b1b3/frappe/utils/print_format_generator.py
