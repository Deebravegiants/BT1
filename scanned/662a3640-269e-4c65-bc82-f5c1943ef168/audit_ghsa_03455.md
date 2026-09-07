# [M] Prototype Pollution in iniparserjs

## Summary
Severity: Medium
Advisory: GHSA-2f6g-w5gj-c93h
CVE: CVE-2021-23328
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-2f6g-w5gj-c93h
Type: github-advisory

## Affected
- npm: `iniparserjs` — affected >=0

## Details
This affects all versions of package iniparserjs. This vulnerability relates when ini_parser.js is concentrating arrays. Depending on if user input is provided, an attacker can overwrite and pollute the object prototype of a program.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23328
- https://snyk.io/vuln/SNYK-JS-INIPARSERJS-1065989
- https://www.npmjs.com/package/iniparserjs
