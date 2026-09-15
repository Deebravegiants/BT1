# [C] ERPNext: Server-Side Template Injection leading to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-65974
Aliases: GHSA-w996-r7v3-87wr
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-65974
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 15.111.0 and 16.22.0, limited authenticated users can cross a permission boundary in Frappe safe execution because frappe.render_template is exposed without forcing restrict_globals, allowing server-side template injection and remote code execution. This issue is fixed in versions 15.111.0 and 16.22.0.

## References
- https://github.com/frappe/erpnext/releases/tag/v15.111.0
- https://github.com/frappe/erpnext/releases/tag/v16.22.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65974.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-w996-r7v3-87wr
- https://nvd.nist.gov/vuln/detail/CVE-2026-65974
- https://github.com/frappe/frappe/commit/529d190a252863672164d10bfcd91d1de0ac1c7c
