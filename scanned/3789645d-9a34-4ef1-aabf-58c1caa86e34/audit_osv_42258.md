# [M] Frappe: Access control bypass via REST API dot-notation fields on linked doctypes

## Summary
Severity: Medium
Advisory: CVE-2026-66003
Aliases: GHSA-p25m-7rvg-6fvr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-66003
Type: osv

## Details
Frappe is a full-stack web application framework written in Python and JavaScript. Prior to version 15.115.0, an access control bypass in the REST API allows a user to read data from Linked DocTypes that they are not authorized to access. When a document references another document through a Link field, the framework does not consistently enforce the linked DocType's own permissions when the record is retrieved through the REST API, so a low-privileged authenticated user can obtain fields from linked records outside their permitted scope. This issue is fixed in version 15.115.0.

## References
- https://github.com/frappe/frappe/releases/tag/v15.115.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66003.json
- https://github.com/frappe/frappe/security/advisories/GHSA-p25m-7rvg-6fvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-66003
