# [H] Directory traversal in convert-svg-core

## Summary
Severity: High
Advisory: GHSA-5f47-rcg5-9m24
CVE: CVE-2022-24278
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-11
Source: https://github.com/advisories/GHSA-5f47-rcg5-9m24
Type: github-advisory

## Affected
- npm: `convert-svg-core` — affected >=0 <0.6.4

## Details
The package convert-svg-core before 0.6.4 is vulnerable to Directory Traversal due to improper sanitization of SVG tags. Exploiting this vulnerability is possible by using a specially crafted SVG file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24278
- https://github.com/neocotic/convert-svg/issues/86
- https://github.com/neocotic/convert-svg/pull/87
- https://github.com/neocotic/convert-svg/commit/2bbc498c5029238637206661dbac9e44d37d17c5
- https://github.com/neocotic/convert-svg
- https://snyk.io/vuln/SNYK-JS-CONVERTSVGCORE-2859830
