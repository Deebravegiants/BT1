# [M] Stage.js DOM Clobbering vulnerabilty

## Summary
Severity: Medium
Advisory: GHSA-fp3m-g5rc-4c28
CVE: CVE-2024-53386
CWE: CWE-79, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-03
Source: https://github.com/advisories/GHSA-fp3m-g5rc-4c28
Type: github-advisory

## Affected
- npm: `stage-js` — affected >=0

## Details
Stage.js through 0.8.10 allows DOM Clobbering (with resultant XSS for untrusted input that contains HTML but does not directly contain JavaScript), because document.currentScript lookup can be shadowed by attacker-injected HTML elements.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53386
- https://gist.github.com/jackfromeast/31d56f1ad17673aabb6ab541e65a5534
- https://github.com/piqnt/stage.js
- https://github.com/piqnt/stage.js/blob/919f6e94b14242f6e6994141a9e1188439d306d5/lib/core.js#L158-L159
