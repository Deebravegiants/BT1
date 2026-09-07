# [H] Code injection via SVG file in convert-svg-core

## Summary
Severity: High
Advisory: GHSA-54px-mhwv-5v8x
CVE: CVE-2022-24429
CWE: CWE-74, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2022-06-11
Source: https://github.com/advisories/GHSA-54px-mhwv-5v8x
Type: github-advisory

## Affected
- npm: `convert-svg-core` — affected >=0 <0.6.3

## Details
The package convert-svg-core before 0.6.3 are vulnerable to Arbitrary Code Injection when using a specially crafted SVG file. An attacker can read arbitrary files from the file system and then show the file content as a converted PNG file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24429
- https://github.com/neocotic/convert-svg/issues/84
- https://github.com/neocotic/convert-svg/commit/a43dffaab0f1e419d5be84e2e7356b86ffac3cf1
- https://github.com/neocotic/convert-svg
- https://snyk.io/vuln/SNYK-JS-CONVERTSVGCORE-2859212
