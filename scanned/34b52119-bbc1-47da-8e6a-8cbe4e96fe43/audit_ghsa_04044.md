# [M] Cross-site Scripting in remarkable

## Summary
Severity: Medium
Advisory: GHSA-36m4-6v6m-4vpr
CVE: CVE-2019-12043
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-05-29
Source: https://github.com/advisories/GHSA-36m4-6v6m-4vpr
Type: github-advisory

## Affected
- npm: `remarkable` — affected >=0 <1.7.2

## Details
In remarkable 1.7.1, lib/parser_inline.js mishandles URL filtering, which allows attackers to trigger XSS via unprintable characters, as demonstrated by a `\x0ejavascript:` URL.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-12043
- https://github.com/jonschlinkert/remarkable/issues/332
- https://github.com/jonschlinkert/remarkable/commit/49e87b7ae2dc323d83606792a749fb207595249e
