# [M] Path Traversal in simplehttpserver

## Summary
Severity: Medium
Advisory: GHSA-vwr2-wj63-86gr
CVE: CVE-2018-16478
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-12-06
Source: https://github.com/advisories/GHSA-vwr2-wj63-86gr
Type: github-advisory

## Affected
- npm: `simplehttpserver` — affected >=0

## Details
All versions of `simplehttpserver` are vulnerable to Path Traversal. 

This vulnerability allows an attacker to access files outside the webroot since it allows symlink navigation in the URL.


## Recommendation

No fix is currently available. Do not use `simplehttpserver` in production or consider using an alternative module until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16478
- https://hackerone.com/reports/403703
- https://github.com/advisories/GHSA-vwr2-wj63-86gr
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/484.json
- https://github.com/tikonen/blog/tree/master/simplehttpserver
- https://www.npmjs.com/advisories/744
