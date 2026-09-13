# [C] Prototype Pollution in confucious

## Summary
Severity: Critical
Advisory: GHSA-fmrr-mx6j-h3h5
CVE: CVE-2020-7714
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-fmrr-mx6j-h3h5
Type: github-advisory

## Affected
- npm: `confucious` — affected >=0

## Details
All versions of package confucious up to and including version 0.0.12 are vulnerable to Prototype Pollution via the set function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7714
- https://snyk.io/vuln/SNYK-JS-CONFUCIOUS-598665
