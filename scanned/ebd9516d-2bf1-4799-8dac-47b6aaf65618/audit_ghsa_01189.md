# [H] Cross-Site Scripting in md-data-table

## Summary
Severity: High
Advisory: GHSA-hgr5-82rc-p936
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-hgr5-82rc-p936
Type: github-advisory

## Affected
- npm: `md-data-table` — affected >=0.0.0

## Details
All versions of `md-data-table` are vulnerable to cross-site scripting (XSS). This vulnerability is exploitable if an attacker has control over data that is rendered by `mdt-row`


## Recommendation

As there is no fix for this vulnerability at this time we recommend either selecting another package to perform this functionality or properly sanitizing all user data prior to rendering with `md-data-table`

## References
- https://www.npmjs.com/advisories/748
