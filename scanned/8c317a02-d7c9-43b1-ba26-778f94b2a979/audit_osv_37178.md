# [H] Frappe: Broken Access Control in DocShare

## Summary
Severity: High
Advisory: CVE-2026-29077
Aliases: GHSA-5h4c-9p23-4c3m
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-29077
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to versions 15.98.0 and 14.100.0, due to a lack of validation when sharing documents, a user could share a document with a permission that they themselves didn't have. This issue has been patched in versions 15.98.0 and 14.100.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29077.json
- https://github.com/frappe/frappe/security/advisories/GHSA-5h4c-9p23-4c3m
- https://nvd.nist.gov/vuln/detail/CVE-2026-29077
