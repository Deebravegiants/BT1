# [C] mysql2 Remote Code Execution (RCE) via the readCodeFor function

## Summary
Severity: Critical
Advisory: GHSA-fpw7-j2hg-69v5
CVE: CVE-2024-21508
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-11
Source: https://github.com/advisories/GHSA-fpw7-j2hg-69v5
Type: github-advisory

## Affected
- npm: `mysql2` — affected >=0 <3.9.4

## Details
Versions of the package mysql2 before 3.9.4 are vulnerable to Remote Code Execution (RCE) via the `readCodeFor` function due to improper validation of the `supportBigNumbers` and `bigNumberStrings` values.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21508
- https://github.com/sidorares/node-mysql2/pull/2572
- https://github.com/sidorares/node-mysql2/commit/74abf9ef94d76114d9a09415e28b496522a94805
- https://blog.slonser.info/posts/mysql2-attacker-configuration
- https://github.com/sidorares/node-mysql2
- https://github.com/sidorares/node-mysql2/blob/1609b5393516d72a4ae47196837317fbe75e0c13/lib/parsers/text_parser.js%23L14C10-L14C21
- https://github.com/sidorares/node-mysql2/releases/tag/v3.9.4
- https://security.snyk.io/vuln/SNYK-JS-MYSQL2-6591085
