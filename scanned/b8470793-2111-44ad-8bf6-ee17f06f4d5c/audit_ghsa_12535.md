# [H] flatnest Prototype Pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-7px2-3c2p-q4v4
CVE: CVE-2023-26135
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-7px2-3c2p-q4v4
Type: github-advisory

## Affected
- npm: `flatnest` — affected >=0

## Details
All versions of the package flatnest are vulnerable to Prototype Pollution via the `nest()` function in `flatnest/nest.js` file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26135
- https://github.com/brycebaril/node-flatnest/issues/4
- https://github.com/brycebaril/node-flatnest/commit/27d569baf9d9d25677640edeaf2d13af165868d6
- https://github.com/brycebaril/node-flatnest
- https://github.com/brycebaril/node-flatnest/blob/b7d97ec64a04632378db87fcf3577bd51ac3ee39/nest.js#L43
- https://github.com/brycebaril/node-flatnest/blob/b7d97ec64a04632378db87fcf3577bd51ac3ee39/nest.js%23L43
- https://security.snyk.io/vuln/SNYK-JS-FLATNEST-3185149
