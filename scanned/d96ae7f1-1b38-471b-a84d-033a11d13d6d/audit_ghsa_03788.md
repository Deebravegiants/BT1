# [M] Path Traversal in http-file-server

## Summary
Severity: Medium
Advisory: GHSA-2mp5-m968-gwr2
CVE: CVE-2019-5447
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2019-07-16
Source: https://github.com/advisories/GHSA-2mp5-m968-gwr2
Type: github-advisory

## Affected
- npm: `http-file-server` — affected >=0

## Details
All versions of `http-file-server` are vulnerable to Path Traversal. The package fails to sanitize URLs, allowing attackers to access server files outside of the served folder using relative paths.


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-5447
- https://hackerone.com/reports/570133
- https://www.npmjs.com/advisories/1077
