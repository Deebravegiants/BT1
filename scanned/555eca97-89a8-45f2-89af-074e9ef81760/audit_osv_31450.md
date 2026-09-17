# [M] Frappe CRM 1.53.1 — Multiple SQL Injections in Dashboard Controller

## Summary
Severity: Medium
Advisory: CVE-2025-11461
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-11-26
Source: https://osv.dev/vulnerability/CVE-2025-11461
Type: osv

## Details
Multiple SQL Injections in Frappe CRM Dashboard Controller due to unsafe concatenation of user-controlled parameters into dynamic SQL statements.
This issue affects Frappe CRM: 1.53.1.

## References
- https://fluidattacks.com/advisories/oz
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11461.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-11461
- https://github.com/frappe/crm/pull/1339
- https://github.com/frappe/crm
