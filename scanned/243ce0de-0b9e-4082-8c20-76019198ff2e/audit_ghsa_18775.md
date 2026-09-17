# [H] Casdoor is vulnerable to Improper Authorization

## Summary
Severity: High
Advisory: GHSA-5m9m-j5p7-m7f9
CVE: CVE-2025-61524
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-08
Source: https://github.com/advisories/GHSA-5m9m-j5p7-m7f9
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0 <2.63.0

## Details
An issue in the permission verification module and organization/application editing interface in Casdoor before 2.63.0 allows remote authenticated administrators of any organization within the system to bypass the system's permission verification mechanism by directly concatenating URLs after login.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-61524
- https://github.com/casdoor/casdoor/commit/d883db907bb6e0b95737ef8e8b57b7da9078cbdd
- https://gist.github.com/DevHjz/e75cea851d48e5f5478ac2a90757851a
- https://github.com/casdoor/casdoor
- https://github.com/casdoor/casdoor/releases/tag/v2.63.0
- http://casdoor.com
