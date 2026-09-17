# [H] SQL Injection in untitled-model

## Summary
Severity: High
Advisory: GHSA-hq8g-qq57-5275
CWE: CWE-89
Ecosystem: npm
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-hq8g-qq57-5275
Type: github-advisory

## Affected
- npm: `untitled-model` — affected >=0

## Details
All versions of `untitled-model` re vulnerable to SQL Injection. Query parameters are not properly sanitized allowing attackers to inject SQL statements and execute arbitrary SQL queries.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://hackerone.com/reports/507222
- https://www.npmjs.com/advisories/989
