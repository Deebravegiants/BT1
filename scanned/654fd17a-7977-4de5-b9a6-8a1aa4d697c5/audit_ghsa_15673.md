# [H] fast-xml-parser vulnerable to ReDOS at currency parsing

## Summary
Severity: High
Advisory: GHSA-mpg4-rc92-vx8v
CVE: CVE-2024-41818
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-29
Source: https://github.com/advisories/GHSA-mpg4-rc92-vx8v
Type: github-advisory

## Affected
- npm: `fast-xml-parser` — affected >=4.3.5 <4.4.1

## Details
### Summary
A ReDOS that exists on currency.js was discovered by Gauss Security Labs R&D team.

### Details
https://github.com/NaturalIntelligence/fast-xml-parser/blob/v4.4.0/src/v5/valueParsers/currency.js#L10 contains a vulnerable regex 

### PoC
pass the following string '\t'.repeat(13337)  + '.'

### Impact
Denial of service during currency parsing in experimental version 5 of fast-xml-parser-library

https://gauss-security.com

## References
- https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-mpg4-rc92-vx8v
- https://nvd.nist.gov/vuln/detail/CVE-2024-41818
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/ba5f35e7680468acd7906eaabb2f69e28ed8b2aa
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/d0bfe8a3a2813a185f39591bbef222212d856164
- https://github.com/NaturalIntelligence/fast-xml-parser
- https://github.com/NaturalIntelligence/fast-xml-parser/blob/master/src/v5/valueParsers/currency.js#L10
