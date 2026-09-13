# [H] Badger Database Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-69r2-2fg7-7hf9
CVE: CVE-2024-36581
CWE: CWE-1321, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-06-17
Source: https://github.com/advisories/GHSA-69r2-2fg7-7hf9
Type: github-advisory

## Affected
- npm: `@abw/badger-database` — affected >=0

## Details
A Prototype Pollution issue in abw badger-database 1.2.1 allows an attacker to execute arbitrary code via dist/badger-database.esm.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36581
- https://gist.github.com/mestrtee/f6b2ed1b3b4bc0df994c7455fc6110bd
- https://github.com/abw/badger-database-js
