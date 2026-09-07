# [M] PrismJS DOM Clobbering vulnerability

## Summary
Severity: Medium
Advisory: GHSA-x7hr-w5r2-h6wg
CVE: CVE-2024-53382
CWE: CWE-79, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-03-03
Source: https://github.com/advisories/GHSA-x7hr-w5r2-h6wg
Type: github-advisory

## Affected
- npm: `prismjs` — affected >=0 <1.30.0

## Details
Prism (aka PrismJS) through 1.29.0 allows DOM Clobbering (with resultant XSS for untrusted input that contains HTML but does not directly contain JavaScript), because document.currentScript lookup can be shadowed by attacker-injected HTML elements.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-53382
- https://github.com/PrismJS/prism/pull/3863
- https://github.com/PrismJS/prism/commit/8e8b9352dac64457194dd9e51096b4772532e53d
- https://gist.github.com/jackfromeast/aeb128e44f05f95828a1a824708df660
- https://github.com/PrismJS/prism
- https://github.com/PrismJS/prism/blob/59e5a3471377057de1f401ba38337aca27b80e03/prism.js#L226-L259
