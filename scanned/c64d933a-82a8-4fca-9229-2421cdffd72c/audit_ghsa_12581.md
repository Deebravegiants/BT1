# [H] fast-xml-parser vulnerable to Regex Injection via Doctype Entities

## Summary
Severity: High
Advisory: GHSA-6w63-h3fj-q4vw
CVE: CVE-2023-34104
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-6w63-h3fj-q4vw
Type: github-advisory

## Affected
- npm: `fast-xml-parser` — affected >=4.1.3 <4.2.4

## Details
### Impact
"fast-xml-parser" allows special characters in entity names, which are not escaped or sanitized. Since the entity name is used for creating a regex for searching and replacing entities in the XML body, an attacker can abuse it for DoS attacks. By crafting an entity name that results in an intentionally bad performing regex and utilizing it in the entity replacement step of the parser, this can cause the parser to stall for an indefinite amount of time.

### Patches
The problem has been resolved in v4.2.4

### Workarounds
Avoid using DOCTYPE parsing by `processEntities: false` option.

## References
- https://github.com/NaturalIntelligence/fast-xml-parser/security/advisories/GHSA-6w63-h3fj-q4vw
- https://nvd.nist.gov/vuln/detail/CVE-2023-34104
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/39b0e050bb909e8499478657f84a3076e39ce76c
- https://github.com/NaturalIntelligence/fast-xml-parser/commit/a4bdced80369892ee413bf08e28b78795a2b0d5b
- https://github.com/NaturalIntelligence/fast-xml-parser
