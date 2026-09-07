# [H] XSS in enshrined/svg-sanitize due to mishandled script and data values in attributes

## Summary
Severity: High
Advisory: GHSA-gf8j-v8x5-h9qp
CVE: CVE-2019-18857
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2020-01-08
Source: https://github.com/advisories/GHSA-gf8j-v8x5-h9qp
Type: github-advisory

## Affected
- Packagist: `enshrined/svg-sanitize` — affected >=0 <0.12.0

## Details
enshrined/svg-sanitize before 0.12.0 mishandles script and data values in attributes, as demonstrated by unexpected whitespace such as in the javascript&#9;:alert substring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18857
- https://github.com/darylldoyle/svg-sanitizer/commit/51ca4b713f3706d6b27769c6296bbc0c28a5bbd0
- https://github.com/darylldoyle/svg-sanitizer
- https://github.com/darylldoyle/svg-sanitizer/compare/0.11.0...0.12.0
