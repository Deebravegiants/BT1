# [M] Cross-site Scripting in edge.js

## Summary
Severity: Medium
Advisory: GHSA-55r9-7mf8-m382
CVE: CVE-2021-23443
CWE: CWE-79, CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-22
Source: https://github.com/advisories/GHSA-55r9-7mf8-m382
Type: github-advisory

## Affected
- npm: `edge.js` — affected >=0 <5.3.2

## Details
Edge is a logical and batteries included template engine for Node.js. This affects the package edge.js before 5.3.2. A type confusion vulnerability can be used to bypass input sanitization when the input to be rendered is an array (instead of a string or a SafeValue), even if `{{ }}` are used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23443
- https://github.com/edge-js/edge/commit/fa2c7fde86327aeae232752e89a6e37e2e469e21
- https://github.com/edge-js/edge
- https://snyk.io/vuln/SNYK-JS-EDGEJS-1579556
