# [M] PostCSS line return parsing error

## Summary
Severity: Medium
Advisory: GHSA-7fh5-64p2-3v2j
CVE: CVE-2023-44270
CWE: CWE-144, CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-09-30
Source: https://github.com/advisories/GHSA-7fh5-64p2-3v2j
Type: github-advisory

## Affected
- npm: `postcss` — affected >=0 <8.4.31

## Details
An issue was discovered in PostCSS before 8.4.31. It affects linters using PostCSS to parse external Cascading Style Sheets (CSS). There may be `\r` discrepancies, as demonstrated by `@font-face{ font:(\r/*);}` in a rule.

This vulnerability affects linters using PostCSS to parse external untrusted CSS. An attacker can prepare CSS in such a way that it will contains parts parsed by PostCSS as a CSS comment. After processing by PostCSS, it will be included in the PostCSS output in CSS nodes (rules, properties) despite being originally included in a comment.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-44270
- https://github.com/github/advisory-database/issues/2820
- https://github.com/postcss/postcss/commit/58cc860b4c1707510c9cd1bc1fa30b423a9ad6c5
- https://github.com/postcss/postcss
- https://github.com/postcss/postcss/blob/main/lib/tokenize.js#L25
- https://github.com/postcss/postcss/releases/tag/8.4.31
- https://lists.debian.org/debian-lts-announce/2024/12/msg00025.html
