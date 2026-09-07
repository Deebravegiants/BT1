# [H] Path Traversal in convert-svg packages

## Summary
Severity: High
Advisory: GHSA-jv7g-9g6q-cxvw
CVE: CVE-2021-23631
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-27
Source: https://github.com/advisories/GHSA-jv7g-9g6q-cxvw
Type: github-advisory

## Affected
- npm: `convert-svg-core` — affected >=0
- npm: `convert-svg-to-png` — affected >=0
- npm: `convert-svg-to-jpeg` — affected >=0

## Details
This affects all versions of package convert-svg-core; all versions of package convert-svg-to-png; all versions of package convert-svg-to-jpeg. Using a specially crafted SVG file, an attacker could read arbitrary files from the file system and then show the file content as a converted PNG file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23631
- https://gist.github.com/legndery/a248350bb25b8502a03c2f407cedeb14
- https://github.com/neocotic/convert-svg
- https://snyk.io/vuln/SNYK-JS-CONVERTSVGCORE-1582785
- https://snyk.io/vuln/SNYK-JS-CONVERTSVGTOJPEG-2348245
- https://snyk.io/vuln/SNYK-JS-CONVERTSVGTOPNG-2348244
