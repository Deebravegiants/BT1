# [M] CVE-2026-17524

## Summary
Severity: Medium
Advisory: CVE-2026-17524
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2026-17524
Type: osv

## Details
Versions of the package zip-lib before 1.1.0 are vulnerable to Directory Traversal via the caching mechanism for path validation during the extraction process. An attacker can bypass security checks designed to prevent directory traversal. The intended security function, isOutsideTargetFolder, only checks and caches the path status when the initial directory symlink is created during the first extraction.

## References
- https://security.snyk.io/vuln/SNYK-JS-ZIPLIB-13834403
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17524.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-17524
- https://github.com/fpsqdb/zip-lib/issues/14
- https://github.com/fpsqdb/zip-lib/commit/0c29b1e17050f2611f4f37e6aaa92a60b3cb89d5
