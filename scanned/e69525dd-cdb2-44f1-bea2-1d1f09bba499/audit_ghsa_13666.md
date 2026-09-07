# [M] Cross-site Scripting in DOMSanitizer

## Summary
Severity: Medium
Advisory: GHSA-2ghm-r75j-pjx2
CVE: CVE-2023-49146
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-11-23
Source: https://github.com/advisories/GHSA-2ghm-r75j-pjx2
Type: github-advisory

## Affected
- Packagist: `rhukster/dom-sanitizer` — affected >=0 <1.0.7

## Details
DOMSanitizer (aka dom-sanitizer) before 1.0.7 allows XSS via an SVG document because of mishandling of comments and greedy regular expressions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49146
- https://github.com/rhukster/dom-sanitizer/commit/c2a98f27ad742668b254282ccc5581871d0fb601
- https://github.com/rhukster/dom-sanitizer
- https://github.com/rhukster/dom-sanitizer/compare/1.0.6...1.0.7
