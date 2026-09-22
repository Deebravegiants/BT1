# [H] body-parser-xml vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-2ghc-6v89-pw9j
CVE: CVE-2021-3666
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2021-09-14
Source: https://github.com/advisories/GHSA-2ghc-6v89-pw9j
Type: github-advisory

## Affected
- npm: `body-parser-xml` — affected >=0 <2.0.3

## Details
body-parser-xml is vulnerable to Improperly Controlled Modification of Object Prototype Attributes ('Prototype Pollution').

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3666
- https://github.com/fiznool/body-parser-xml/commit/d46ca622560f7c9a033cd9321c61e92558150d63
- https://github.com/fiznool/body-parser-xml
- https://huntr.dev/bounties/1-other-fiznool/body-parser-xml
