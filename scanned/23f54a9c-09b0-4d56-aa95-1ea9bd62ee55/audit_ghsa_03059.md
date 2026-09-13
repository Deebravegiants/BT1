# [C] Prototype Pollution in irrelon-path and @irrelon/path

## Summary
Severity: Critical
Advisory: GHSA-j7cg-h9v9-6vqp
CVE: CVE-2020-7708
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-j7cg-h9v9-6vqp
Type: github-advisory

## Affected
- npm: `irrelon-path` — affected >=0 <4.7.0
- npm: `@irrelon/path` — affected >=0 <4.7.0

## Details
The package irrelon-path before 4.7.0; the package @irrelon/path before 4.7.0 are vulnerable to Prototype Pollution via the set, unSet, pushVal and pullVal functions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7708
- https://github.com/Irrelon/irrelon-path/commit/8a126b160c1a854ae511659c111413ad9910ebe3
- https://github.com/Irrelon/irrelon-path
- https://snyk.io/vuln/SNYK-JS-IRRELONPATH-598672
- https://snyk.io/vuln/SNYK-JS-IRRELONPATH-598673
