# [M] mysql2 vulnerable to Prototype Poisoning

## Summary
Severity: Medium
Advisory: GHSA-49j4-86m8-q2jw
CVE: CVE-2024-21509
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-49j4-86m8-q2jw
Type: github-advisory

## Affected
- npm: `mysql2` — affected >=0 <3.9.4

## Details
Versions of the package mysql2 before 3.9.4 are vulnerable to Prototype Poisoning due to insecure results object creation and improper user input sanitization passed through `parserFn` in `text_parser.js` and `binary_parser.js`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21509
- https://github.com/sidorares/node-mysql2/pull/2574
- https://github.com/sidorares/node-mysql2/commit/4a964a3910a4b8de008696c554ab1b492e9b4691
- https://blog.slonser.info/posts/mysql2-attacker-configuration
- https://github.com/sidorares/node-mysql2
- https://github.com/sidorares/node-mysql2/blob/fd3d117da82cc5c5fa5a3701d7b33ca77691bc61/lib/parsers/text_parser.js%23L134
- https://github.com/sidorares/node-mysql2/releases/tag/v3.9.4
- https://security.snyk.io/vuln/SNYK-JS-MYSQL2-6591084
