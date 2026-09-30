# [H] Frappe Helpdesk 1.14.0 — SQL Injection in dashboard get_dashboard_data

## Summary
Severity: High
Advisory: CVE-2025-10655
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-10655
Type: osv

## Details
SQL Injection in Frappe HelpDesk in the dashboard get_dashboard_data due to unsafe concatenation of user-controlled parameters into dynamic SQL statements.This issue affects Frappe HelpDesk: 1.14.0.

## References
- https://fluidattacks.com/advisories/dyango
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10655.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-10655
- https://github.com/frappe/helpdesk/pull/2795
- https://github.com/frappe/helpdesk
