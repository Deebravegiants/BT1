# [M] Predictable results in nanoid generation when given non-integer values

## Summary
Severity: Medium
Advisory: GHSA-mwcw-c2x4-8c55
CVE: CVE-2024-55565
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-12-09
Source: https://github.com/advisories/GHSA-mwcw-c2x4-8c55
Type: github-advisory

## Affected
- npm: `nanoid` — affected >=4.0.0 <5.0.9
- npm: `nanoid` — affected >=0 <3.3.8

## Details
When nanoid is called with a fractional value, there were a number of undesirable effects:

1. in browser and non-secure, the code infinite loops on while (size--)
2. in node, the value of poolOffset becomes fractional, causing calls to nanoid to return zeroes until the pool is next filled
3. if the first call in node is a fractional argument, the initial buffer allocation fails with an error

Version 3.3.8 and 5.0.9 are fixed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-55565
- https://github.com/ai/nanoid/pull/510
- https://github.com/ai/nanoid
- https://github.com/ai/nanoid/compare/3.3.7...3.3.8
- https://github.com/ai/nanoid/releases/tag/5.0.9
- https://lists.debian.org/debian-lts-announce/2024/12/msg00025.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00006.html
