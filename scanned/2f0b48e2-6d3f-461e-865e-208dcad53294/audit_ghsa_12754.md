# [H] Servst vulnerable to Path Traversal

## Summary
Severity: High
Advisory: GHSA-88v8-v46g-6c9w
CVE: CVE-2022-25936
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-30
Source: https://github.com/advisories/GHSA-88v8-v46g-6c9w
Type: github-advisory

## Affected
- npm: `servst` — affected >=0 <2.0.3

## Details
Versions of the package servst before 2.0.3 are vulnerable to Directory Traversal due to improper sanitization of its filePath variable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25936
- https://github.com/andrepolischuk/servst/commit/f7cae5d2d7c64c86bc512e1e50614240396ef114
- https://gist.github.com/lirantal/691d02d607753d54856f9335f9a1692f
- https://github.com/andrepolischuk/servst
- https://security.snyk.io/vuln/SNYK-JS-SERVST-3244896
