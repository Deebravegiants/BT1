# [H] SQL Injection in Casdoor

## Summary
Severity: High
Advisory: GHSA-m358-g4rp-533r
CVE: CVE-2022-24124
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-m358-g4rp-533r
Type: github-advisory

## Affected
- Go: `github.com/casdoor/casdoor` — affected >=0 <1.13.1

## Details
The query API in Casdoor before 1.13.1 has a SQL injection vulnerability related to the field and value parameters, as demonstrated by api/get-organizations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24124
- https://github.com/casdoor/casdoor/issues/439
- https://github.com/casdoor/casdoor/pull/442
- https://github.com/casdoor/casdoor/commit/5ec0c7a89005819960d8fe07f5ddda13d1371b8c
- https://github.com/casdoor/casdoor
- https://github.com/casdoor/casdoor/compare/v1.13.0...v1.13.1
- http://packetstormsecurity.com/files/166163/Casdoor-1.13.0-SQL-Injection.html
