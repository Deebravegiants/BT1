# [H] Missing Origin Validation in webpack-dev-server

## Summary
Severity: High
Advisory: GHSA-cf66-xwfp-gvc4
CVE: CVE-2018-14732
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-01-04
Source: https://github.com/advisories/GHSA-cf66-xwfp-gvc4
Type: github-advisory

## Affected
- npm: `webpack-dev-server` — affected >=0 <3.1.11

## Details
Versions of `webpack-dev-server` before 3.1.10 are missing origin validation on the websocket server. This vulnerability allows a remote attacker to steal a developer's source code because the origin of requests to the websocket server that is used for Hot Module Replacement (HMR) are not validated.


## Recommendation
For `webpack-dev-server` update to version 3.1.11 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-14732
- https://github.com/webpack/webpack-dev-server/issues/1445
- https://github.com/webpack/webpack-dev-server/issues/1620
- https://github.com/webpack/webpack-dev-server/commit/f18e5adf123221a1015be63e1ca2491ca45b8d10
- https://github.com/webpack/webpack-dev-server
- https://github.com/webpack/webpack-dev-server/blob/master/CHANGELOG.md#3111-2018-12-21
- https://www.npmjs.com/advisories/725
