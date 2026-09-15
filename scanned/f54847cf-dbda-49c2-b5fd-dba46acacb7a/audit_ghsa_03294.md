# [C] Prototype Pollution in gammautils

## Summary
Severity: Critical
Advisory: GHSA-pgmg-gf5p-54j8
CVE: CVE-2020-7718
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-pgmg-gf5p-54j8
Type: github-advisory

## Affected
- npm: `gammautils` — affected >=0

## Details
All versions of package gammautils up to and including version 0.0.81 are vulnerable to Prototype Pollution via the `deepSet` and `deepMerge` functions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7718
- https://snyk.io/vuln/SNYK-JS-GAMMAUTILS-598670
