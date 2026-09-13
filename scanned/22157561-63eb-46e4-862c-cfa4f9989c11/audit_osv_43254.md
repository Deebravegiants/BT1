# [C] ERPNext: Possibility of server-side template injection due to missing validation

## Summary
Severity: Critical
Advisory: CVE-2026-72911
Aliases: GHSA-qq49-v74j-hjh7
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72911
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 15.118.0 and 16.29.0, the validate_template and render_template calls in erpnext/accounts/doctype/process_statement_of_accounts/process_statement_of_accounts.py render subject, body, and pdf_name fields with unrestricted globals including frappe.utils, allowing an authenticated user with a common operational role to inject template expressions, execute arbitrary server-side code, and read data across the application. This issue is fixed in versions 15.118.0 and 16.29.0.

## References
- https://github.com/frappe/erpnext/releases/tag/v15.118.0
- https://github.com/frappe/erpnext/releases/tag/v16.29.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72911.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-qq49-v74j-hjh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-72911
- https://github.com/frappe/erpnext/commit/5f6952b15c1f6ee893770d5bc618558a6ba41a28
- https://github.com/frappe/erpnext/commit/88443e4a97c6c0a40d85a9e6785577191296ee39
- https://github.com/frappe/erpnext/commit/ecb6d48ec025e0c94abac35b2e4f7607f4c86465
- https://github.com/frappe/erpnext/pull/56458
