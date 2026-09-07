# [M] SQL Injection in sql

## Summary
Severity: Medium
Advisory: GHSA-8f93-rv4p-x4jw
CWE: CWE-89
Ecosystem: npm
Published: 2019-06-12
Source: https://github.com/advisories/GHSA-8f93-rv4p-x4jw
Type: github-advisory

## Affected
- npm: `sql` — affected >=0

## Details
All versions of `sql` are vulnerable to sql injection as it does not properly escape parameters when building SQL queries.


## Recommendation

No fix is currently available for this vulnerability. It is our recommendation to not install or use this module until a fix is available.

## References
- https://hackerone.com/reports/319465
- https://www.npmjs.com/advisories/662
