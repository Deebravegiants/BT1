# [M] ERPNext v16.25.0 - Improper authorization in Prospect opportunities API

## Summary
Severity: Medium
Advisory: CVE-2026-13227
Aliases: GHSA-g8r3-82j6-wp48
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-13227
Type: osv

## Details
An Improper Authorization vulnerability exists in ERPNext version <v16.25.0 and <15.115.0  due to insufficient access control in the whitelisted API method erpnext.crm.doctype.prospect.prospect.get_opportunities.

This issue affects ERPNext: before 15.115.0, before 16.26.0.

## References
- https://fluidattacks.com/es/advisories/kraviz
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13227.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-g8r3-82j6-wp48
- https://nvd.nist.gov/vuln/detail/CVE-2026-13227
- https://github.com/frappe/erpnext/releases?page=2#release-v15.115.0
- https://github.com/frappe/erpnext/releases?page=2#release-v16.26.0
- https://github.com/frappe/erpnext
