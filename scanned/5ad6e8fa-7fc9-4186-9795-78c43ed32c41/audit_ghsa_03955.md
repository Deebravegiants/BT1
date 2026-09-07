# [H] SQL Injection in waterline-sequel

## Summary
Severity: High
Advisory: GHSA-cgpp-wm2h-6hqx
CVE: CVE-2016-10551
CWE: CWE-89
Ecosystem: npm
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-cgpp-wm2h-6hqx
Type: github-advisory

## Affected
- npm: `waterline-sequel` — affected >=0 <0.5.1

## Details
Affected versions of `waterline-sequel` are vulnerable to SQL injection in cases where user input is passed into the `like`, `contains`, `startsWith`, or `endsWith` methods.



## Recommendation

Upgrade to at least version 0.5.1

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10551
- https://github.com/balderdashy/waterline/issues/1219#issuecomment-157294530
- https://github.com/balderdashy/waterline-sequel/pull/66
- https://github.com/advisories/GHSA-cgpp-wm2h-6hqx
- https://www.npmjs.com/advisories/115
