# [C] plotly.js prototype pollution vulnerability

## Summary
Severity: Critical
Advisory: GHSA-wjc4-73q6-gv3m
CVE: CVE-2023-46308
CWE: CWE-1321
Ecosystem: Packagist, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-wjc4-73q6-gv3m
Type: github-advisory

## Affected
- Packagist: `plotly/plotly.js` — affected >=0 <2.25.2
- npm: `plotly.js` — affected >=0 <2.25.2

## Details
In Plotly plotly.js before 2.25.2, plot API calls have a risk of __proto__ being polluted in expandObjectPaths or nestedProperty.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46308
- https://github.com/plotly/plotly.R/issues/2463
- https://github.com/plotly/plotly.js/commit/02498404c8ad7a3395191e65694fb142a37b0fe9
- https://github.com/plotly/plotly.js/commit/5efd2a1f07a418b230a5626fc6c1c7929c47949d
- https://github.com/plotly/plotly.js
- https://github.com/plotly/plotly.js/releases/tag/v2.25.2
- https://plotly.com/javascript
