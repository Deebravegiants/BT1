# [H] Path Traversal in algo-httpserv

## Summary
Severity: High
Advisory: GHSA-cgjv-rghq-qhgp
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2019-09-11
Source: https://github.com/advisories/GHSA-cgjv-rghq-qhgp
Type: github-advisory

## Affected
- npm: `algo-httpserv` — affected >=0 <1.1.2

## Details
Versions of `algo-httpserv` prior to 1.1.2 are vulnerable to Path Traversal.  Due to insufficient input sanitization, attackers can access server files by using relative paths. 


## Recommendation

Upgrade to version 1.1.2 or later.

## References
- https://github.com/AlgoRythm-Dylan/httpserv/commit/bcfe9d4316c2b59aab3a64a38905376026888735
- https://snyk.io/vuln/SNYK-JS-ALGOHTTPSERV-174741
- https://www.npmjs.com/advisories/889
