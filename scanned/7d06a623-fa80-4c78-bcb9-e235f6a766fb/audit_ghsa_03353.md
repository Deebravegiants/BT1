# [M] Improper Input Validation in SocksJS-Node

## Summary
Severity: Medium
Advisory: GHSA-c9g6-9335-x697
CVE: CVE-2020-7693
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-c9g6-9335-x697
Type: github-advisory

## Affected
- npm: `sockjs` — affected >=0 <0.3.20

## Details
Incorrect handling of Upgrade header with the value websocket leads in crashing of containers hosting sockjs apps. This affects the package sockjs before 0.3.20.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7693
- https://github.com/sockjs/sockjs-node/issues/252
- https://github.com/sockjs/sockjs-node/pull/265
- https://github.com/sockjs/sockjs-node/commit/dd7e642cd69ee74385825816d30642c43e051d16
- https://github.com/andsnw/sockjs-dos-py
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-575448
- https://snyk.io/vuln/SNYK-JS-SOCKJS-575261
- https://www.npmjs.com/package/sockjs
