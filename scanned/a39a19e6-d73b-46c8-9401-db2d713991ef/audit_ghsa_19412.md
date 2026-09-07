# [M] expand-object Vulnerable to Prototype Pollution via the expand() Function

## Summary
Severity: Medium
Advisory: GHSA-4vjr-hfpp-2m7w
CVE: CVE-2025-3197
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-04-04
Source: https://github.com/advisories/GHSA-4vjr-hfpp-2m7w
Type: github-advisory

## Affected
- npm: `expand-object` — affected >=0

## Details
Versions of the package expand-object from 0.0.0 to 0.4.2 are vulnerable to Prototype Pollution in the expand() function in index.js. This function expands the given string into an object and allows a nested property to be set without checking the provided keys for sensitive properties like __proto__.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3197
- https://gist.github.com/miguelafmonteiro/d8f66af61d14e06338b688f90c4dfa7c
- https://github.com/jonschlinkert/expand-object
- https://github.com/jonschlinkert/expand-object/blob/master/index.js#L13
- https://security.snyk.io/vuln/SNYK-JS-EXPANDOBJECT-5821390
