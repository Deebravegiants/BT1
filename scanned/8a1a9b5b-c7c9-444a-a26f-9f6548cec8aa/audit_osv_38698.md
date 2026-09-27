# [M] Frappe: Possible Path Traversal and Local File Inclusion via Chrome PDF Generator

## Summary
Severity: Medium
Advisory: CVE-2026-41482
Aliases: GHSA-234v-jfr8-v2f8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-41482
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to 16.18.3, possible path traversal and local file inclusion were possible through secure local resource access in the Chrome PDF Generator. This issue is fixed in version 16.18.3.

## References
- https://github.com/frappe/frappe/releases/tag/v16.18.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41482.json
- https://github.com/frappe/frappe/security/advisories/GHSA-234v-jfr8-v2f8
- https://nvd.nist.gov/vuln/detail/CVE-2026-41482
- https://github.com/frappe/frappe/commit/11066591ed7aa91a7b742f3f689277a90e620ce0
- https://github.com/frappe/frappe/commit/46841f7fde3954e1d3b3a7e248a6d6022343e657
- https://github.com/frappe/frappe/pull/38643
- https://github.com/frappe/frappe/pull/39396
