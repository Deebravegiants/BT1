# [H] SQL Injection in resquel

## Summary
Severity: High
Advisory: GHSA-crpm-fm48-chj7
CWE: CWE-89
Ecosystem: npm
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-crpm-fm48-chj7
Type: github-advisory

## Affected
- npm: `resquel` — affected >=0

## Details
All versions of `resquel` are vulnerable to SQL Injection. Query parameters are not properly sanitized, allowing attackers to inject SQL statements and execute arbitrary SQL queries


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/963
