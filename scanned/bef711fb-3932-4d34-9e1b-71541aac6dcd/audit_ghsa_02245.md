# [M] Cross-site Scripting in curly-bracket-parser

## Summary
Severity: Medium
Advisory: GHSA-rqf8-8c89-mw29
CVE: CVE-2021-23416
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-08-10
Source: https://github.com/advisories/GHSA-rqf8-8c89-mw29
Type: github-advisory

## Affected
- npm: `curly-bracket-parser` — affected >=0

## Details
This affects all versions of package curly-bracket-parser.
 When used as a template library, it does not properly sanitize the user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23416
- https://github.com/magynhard/curly-bracket-parser
- https://github.com/magynhard/curly-bracket-parser/blob/master/src/curly-bracket-parser/curly-bracket-parser.js#23L31
- https://github.com/magynhard/curly-bracket-parser/blob/master/src/curly-bracket-parser/curly-bracket-parser.js%23L31
- https://snyk.io/vuln/SNYK-JS-CURLYBRACKETPARSER-1297106
