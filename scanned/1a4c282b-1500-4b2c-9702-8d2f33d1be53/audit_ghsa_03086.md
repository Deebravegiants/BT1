# [C] Prototype Pollution in promisehelpers

## Summary
Severity: Critical
Advisory: GHSA-rj5f-7c8x-gjg4
CVE: CVE-2020-7723
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-rj5f-7c8x-gjg4
Type: github-advisory

## Affected
- npm: `promisehelpers` — affected >=0

## Details
All versions of package promisehelpers up to and including version 0.0.5 are vulnerable to Prototype Pollution via the insert function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7723
- https://snyk.io/vuln/SNYK-JS-PROMISEHELPERS-598686
