# [C] Prototype Pollution in node-oojs

## Summary
Severity: Critical
Advisory: GHSA-j4rw-x3vg-c8r7
CVE: CVE-2020-7721
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-j4rw-x3vg-c8r7
Type: github-advisory

## Affected
- npm: `node-oojs` — affected >=0

## Details
All versions of package node-oojs up to and including version 1.4.0 are vulnerable to Prototype Pollution via the setPath function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7721
- https://snyk.io/vuln/SNYK-JS-NODEOOJS-598678
