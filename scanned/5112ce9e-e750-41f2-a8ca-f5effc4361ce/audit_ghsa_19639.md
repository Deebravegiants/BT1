# [H] canvg Prototype Pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-v2mw-5mch-w8c5
CVE: CVE-2025-25977
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-03-10
Source: https://github.com/advisories/GHSA-v2mw-5mch-w8c5
Type: github-advisory

## Affected
- npm: `canvg` — affected >=4.0.0 <4.0.3
- npm: `canvg` — affected >=0 <3.0.11

## Details
An issue in canvg prior to v.4.0.3 and v3.0.11 can lead to prototype pollution via the Constructor of the class StyleElement.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-25977
- https://github.com/canvg/canvg/issues/1749
- https://github.com/canvg/canvg/commit/c3743e6345f3e01aefdcdd412c3f26494f4b5d7d
- https://github.com/canvg/canvg
- https://github.com/canvg/canvg/blob/937668eced93e0335c67a255d0d2277ea708b2cb/src/Document/StyleElement.ts
