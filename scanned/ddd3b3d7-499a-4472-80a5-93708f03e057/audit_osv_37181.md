# [M] Frappe: Possibility of SQL Injection due to improper fieldname sanitization

## Summary
Severity: Medium
Advisory: CVE-2026-29081
Aliases: GHSA-w3g7-m7xr-2w38
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-29081
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to versions 14.100.1 and 15.100.0, an endpoint was vulnerable to SQL injection through specially crafted requests, which would allow a malicious actor to extract sensitive information. This issue has been patched in versions 14.100.1 and 15.100.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29081.json
- https://github.com/frappe/frappe/security/advisories/GHSA-w3g7-m7xr-2w38
- https://nvd.nist.gov/vuln/detail/CVE-2026-29081
