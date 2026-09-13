# [M] component-flatten vulnerable to Prototype Pollution

## Summary
Severity: Medium
Advisory: GHSA-g6r3-hhg9-qf58
CVE: CVE-2019-10794
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-g6r3-hhg9-qf58
Type: github-advisory

## Affected
- npm: `component-flatten` — affected >=0

## Details
All versions of component-flatten are vulnerable to Prototype Pollution. The a function could be tricked into adding or modifying properties of Object.prototype using a `__proto__` payload.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10794
- https://github.com/componentjs/flatten.js
- https://snyk.io/vuln/SNYK-JS-COMPONENTFLATTEN-548907
