# [C] Blackprint @blackprint/engine Prototype Pollution issue

## Summary
Severity: Critical
Advisory: GHSA-g3q2-vcjq-rgrc
CVE: CVE-2024-24294
CWE: CWE-1321, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-g3q2-vcjq-rgrc
Type: github-advisory

## Affected
- npm: `@blackprint/engine` — affected >=0.8.12 <0.9.2

## Details
A Prototype Pollution issue in Blackprint @blackprint/engine 0.8.12 through 0.9.1 allows an attacker to execute arbitrary code via the `_utils.setDeepProperty` function of `engine.min.js`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-24294
- https://github.com/Blackprint/engine-js/commit/bd6b965b03c467e7a58ab0cb89b9172fa5e07013
- https://gist.github.com/mestrtee/d1eb6e1f7c6dd60d8838c3e56cab634d
- https://github.com/Blackprint/engine-js
