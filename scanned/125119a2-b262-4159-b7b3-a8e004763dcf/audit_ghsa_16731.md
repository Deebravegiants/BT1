# [H] json-schema-ref-parser Prototype Pollution issue

## Summary
Severity: High
Advisory: GHSA-5f97-h2c2-826q
CVE: CVE-2024-29651
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-20
Source: https://github.com/advisories/GHSA-5f97-h2c2-826q
Type: github-advisory

## Affected
- npm: `@apidevtools/json-schema-ref-parser` — affected >=11.0.0 <11.2.0

## Details
A Prototype Pollution issue in API Dev Tools json-schema-ref-parser v.11.0.0 and v.11.1.0 allows a remote attacker to execute arbitrary code via the `bundle()`, `parse()`, `resolve()`, `dereference()` functions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29651
- https://github.com/APIDevTools/json-schema-ref-parser/commit/8cad7f72c15b198f4d0b5b1c8a3a979b2e4baa82
- https://gist.github.com/tariqhawis/5db76b38112bba756615b688c32409ad
- https://github.com/APIDevTools/json-schema-ref-parser
