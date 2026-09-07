# [M] Cross-site Scripting in teddy

## Summary
Severity: Medium
Advisory: GHSA-5f38-9jw2-6r6h
CVE: CVE-2021-23447
CWE: CWE-79, CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-5f38-9jw2-6r6h
Type: github-advisory

## Affected
- npm: `teddy` — affected >=0 <0.5.9

## Details
Teddy is a readable and easy to learn templating language. This affects the package teddy before 0.5.9. A type confusion vulnerability can be used to bypass input sanitization when the model content is an array (instead of a string).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23447
- https://github.com/rooseveltframework/teddy/pull/518
- https://github.com/rooseveltframework/teddy/commit/64c556717b4879bf8d4c30067cf6e70d899a3dc0
- https://github.com/rooseveltframework/teddy
- https://github.com/rooseveltframework/teddy/releases/tag/0.5.9
- https://snyk.io/vuln/SNYK-JS-TEDDY-1579557
