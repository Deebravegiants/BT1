# [M] Joomla! CMS vulnerable to XSS via the input filter

## Summary
Severity: Medium
Advisory: GHSA-fm22-g2q9-j3pw
CVE: CVE-2025-54476
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:L/VI:L/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-30
Source: https://github.com/advisories/GHSA-fm22-g2q9-j3pw
Type: github-advisory

## Affected
- Packagist: `joomla/filter` — affected >=4.0.0 <4.0.1
- Packagist: `joomla/filter` — affected >=3.0.0 <3.0.5
- Packagist: `joomla/filter` — affected >=0 <2.0.6

## Details
Improper handling of input could lead to a cross-site scripting (XSS) vector in the checkAttribute method of the input filter framework class.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-54476
- https://github.com/joomla-framework/filter/commit/188dd3fccd6fa0532d105a52736affdf6b166217
- https://github.com/joomla-framework/filter/commit/852c7e101c649500d3af58ffb8baf15d7c86d825
- https://github.com/joomla-framework/filter/commit/fcde280785f188e93530f7da68102f7dd8f9f723
- https://developer.joomla.org/security-centre/1010-20250901-core-inadequate-content-filtering-within-the-checkattribute-filter-code.html
- https://github.com/joomla/joomla-cms
