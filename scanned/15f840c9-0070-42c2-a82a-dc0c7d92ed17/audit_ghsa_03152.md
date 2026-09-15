# [C] Prototype Pollution in gedi

## Summary
Severity: Critical
Advisory: GHSA-jh2m-j8pp-55rc
CVE: CVE-2020-7727
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-jh2m-j8pp-55rc
Type: github-advisory

## Affected
- npm: `gedi` — affected >=0

## Details
All versions of package gedi up to and including version 1.6.3 are vulnerable to Prototype Pollution via the set function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7727
- https://snyk.io/vuln/SNYK-JS-GEDI-598803
