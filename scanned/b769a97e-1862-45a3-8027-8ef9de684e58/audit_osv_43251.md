# [M] ERPNext: Broken Access Control on certain endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-72907
Aliases: GHSA-94v6-784v-24q5
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-72907
Type: osv

## Details
ERPNext is a free and open source Enterprise Resource Planning tool. Prior to 15.111.0 and 16.22.0, the add_ac function in erpnext/accounts/utils.py accepts the ignore_permissions argument without enforcing Account create permission, allowing an authenticated limited user to create unauthorized accounting master records and affect financial data integrity and audit trails. This issue is fixed in versions 15.111.0 and 16.22.0.

## References
- https://github.com/frappe/erpnext/releases/tag/v15.111.0
- https://github.com/frappe/erpnext/releases/tag/v16.22.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72907.json
- https://github.com/frappe/erpnext/security/advisories/GHSA-94v6-784v-24q5
- https://nvd.nist.gov/vuln/detail/CVE-2026-72907
- https://github.com/frappe/erpnext/commit/2d0e3fd9af521e407be35fd09e9427176609513f
- https://github.com/frappe/erpnext/commit/37d2adc74ba91f388194b3bbe07368c40573a9b2
- https://github.com/frappe/erpnext/commit/c0cf9aa1a7f95ee22b99ea1ca2a2cb09b314e67f
- https://github.com/frappe/erpnext/pull/55665
