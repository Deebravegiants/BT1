# [H] Remote Code Execution in node-os-utils

## Summary
Severity: High
Advisory: GHSA-j9f8-8h89-j69x
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2019-06-11
Source: https://github.com/advisories/GHSA-j9f8-8h89-j69x
Type: github-advisory

## Affected
- npm: `node-os-utils` — affected >=0 <1.1.0

## Details
Versions of `node-os-utils` prior to 1.1.0 are vulnerable to Remote Code Execution. Due to insufficient input validation an attacker could run arbitrary commands on the server thus rendering the package vulnerable to Remote Code Execution.


## Recommendation

Upgrade to version 1.1.0 or later.

## References
- https://github.com/SunilWang/node-os-utils/issues/2
- https://snyk.io/vuln/SNYK-JS-NODEOSUTILS-173696
- https://www.npmjs.com/advisories/784
