# [M] Frappe: Path Traversal via /backups Route

## Summary
Severity: Medium
Advisory: CVE-2026-42219
Aliases: GHSA-w4p4-fp9m-47gj
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-42219
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to 16.19.0 and 15.109.0, path traversal via download_backups was possible due to lack of hardening. This issue is fixed in versions 16.19.0 and 15.109.0.

## References
- https://github.com/frappe/frappe/releases/tag/v15.109.0
- https://github.com/frappe/frappe/releases/tag/v16.19.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42219.json
- https://github.com/frappe/frappe/security/advisories/GHSA-w4p4-fp9m-47gj
- https://nvd.nist.gov/vuln/detail/CVE-2026-42219
- https://github.com/frappe/frappe/commit/4358f5bd449710027724a1679950d4ea65da6dcc
- https://github.com/frappe/frappe/commit/a470a1189132984635e2ec148f87de5232f5535d
- https://github.com/frappe/frappe/commit/a562ef2a5a3885895b9f9cf14d5a53e32e52d326
- https://github.com/frappe/frappe/pull/38740
- https://github.com/frappe/frappe/pull/39402
- https://github.com/frappe/frappe/pull/39403
