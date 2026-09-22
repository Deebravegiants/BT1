# [M] Path Traversal in m-server

## Summary
Severity: Medium
Advisory: GHSA-vc6r-4x6g-mmqc
CWE: CWE-22
Ecosystem: npm
Published: 2019-06-11
Source: https://github.com/advisories/GHSA-vc6r-4x6g-mmqc
Type: github-advisory

## Affected
- npm: `m-server` — affected >=0 <1.4.2

## Details
Versions of `m-server` before 1.4.2 are vulnerable to path traversal allowing a remote attacker to display content of arbitrary files from the server.


## Recommendation

Update to version 1.4.2 or later.

## References
- https://github.com/nunnly/m-server/commit/01f13f040d1961ca3146dce7e2db990156e65e9a
- https://hackerone.com/reports/319795
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/468.json
- https://www.npmjs.com/advisories/731
