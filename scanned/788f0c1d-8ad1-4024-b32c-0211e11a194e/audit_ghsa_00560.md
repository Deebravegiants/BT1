# [H] Path Traversal in knightjs

## Summary
Severity: High
Advisory: GHSA-3hvm-hgpw-rx4j
CVE: CVE-2018-16475
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-11-06
Source: https://github.com/advisories/GHSA-3hvm-hgpw-rx4j
Type: github-advisory

## Affected
- npm: `knightjs` — affected >=0

## Details
All versions of `knightjs` are vulnerable to Path Traversal. 

This vulnerability allows an attacker to read content of arbitrary files on the server due to lack of input validation.


## Recommendation

As there is currently no fix for this module we recommend not using this module in production environments.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16475
- https://hackerone.com/reports/403707
- https://github.com/advisories/GHSA-3hvm-hgpw-rx4j
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/484.json
- https://www.npmjs.com/advisories/743
