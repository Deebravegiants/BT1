# [H] Certain Frappe requests are vulnerable to Path Traversal

## Summary
Severity: High
Advisory: CVE-2025-68953
Aliases: GHSA-xj39-3g4p-f46v
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-05
Source: https://osv.dev/vulnerability/CVE-2025-68953
Type: osv

## Details
Frappe is a full-stack web application framework. Versions 14.99.5 and below and 15.0.0 through 15.80.1 include requests that are vulnerable to path traversal attacks. Arbitrary files from the server could be retrieved due to a lack of proper sanitization on some requests. This issue is fixed in versions 14.99.6 and 15.88.1. To workaround, changing the setup to use a reverse proxy is recommended.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68953.json
- https://github.com/frappe/frappe/security/advisories/GHSA-xj39-3g4p-f46v
- https://nvd.nist.gov/vuln/detail/CVE-2025-68953
- https://github.com/frappe/frappe/commit/3867fb112c3f7be1a863e40f19e9235719f784fb
- https://github.com/frappe/frappe/commit/959efd6a498cfaeaf7d4e0ab6cca78c36192d34d
