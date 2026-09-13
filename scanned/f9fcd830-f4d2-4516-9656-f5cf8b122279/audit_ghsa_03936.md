# [H] Path Traversal in simplehttpserver

## Summary
Severity: High
Advisory: GHSA-45j8-pm75-5v8x
CVE: CVE-2018-16493
CWE: CWE-548
Ecosystem: npm
Published: 2019-02-07
Source: https://github.com/advisories/GHSA-45j8-pm75-5v8x
Type: github-advisory

## Affected
- npm: `static-resource-server` — affected >=0

## Details
Versions of `simplehttpserver` prior to 0.2.1 are vulnerable to Path Traversal.  Due to insufficient input sanitization, attackers can access server files by using relative paths. 


## Recommendation

Upgrade to version 0.2.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16493
- https://hackerone.com/reports/357109
- https://hackerone.com/reports/432600
- https://github.com/advisories/GHSA-45j8-pm75-5v8x
- https://www.npmjs.com/advisories/967
- https://www.npmjs.com/advisories/968
