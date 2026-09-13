# [C] Prototype Pollution in dot-notes

## Summary
Severity: Critical
Advisory: GHSA-qr4m-jcvc-3382
CVE: CVE-2020-7717
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-qr4m-jcvc-3382
Type: github-advisory

## Affected
- npm: `dot-notes` — affected >=0

## Details
All versions of package dot-notes up to and including version 3.2.0 are vulnerable to Prototype Pollution via the create function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7717
- https://snyk.io/vuln/SNYK-JS-DOTNOTES-598668
