# [C] Prototype Pollution in nis-utils

## Summary
Severity: Critical
Advisory: GHSA-gr58-j5wh-m333
CVE: CVE-2020-7703
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-gr58-j5wh-m333
Type: github-advisory

## Affected
- npm: `nis-utils` — affected >=0

## Details
All versions of package nis-utils up to and including 0.6.10 are vulnerable to Prototype Pollution via the setValue function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7703
- https://snyk.io/vuln/SNYK-JS-NISUTILS-598799
