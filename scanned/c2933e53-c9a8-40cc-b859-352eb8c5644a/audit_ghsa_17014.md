# [H] SheetJS Regular Expression Denial of Service (ReDoS)

## Summary
Severity: High
Advisory: GHSA-5pgg-2g8v-p4x9
CVE: CVE-2024-22363
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-05
Source: https://github.com/advisories/GHSA-5pgg-2g8v-p4x9
Type: github-advisory

## Affected
- npm: `xlsx` — affected >=0

## Details
SheetJS Community Edition before 0.20.2 is vulnerable.to Regular Expression Denial of Service (ReDoS).

A non-vulnerable version cannot be found via npm, as the repository hosted on GitHub and the npm package `xlsx` are no longer maintained. Version 0.20.2 can be downloaded via https://cdn.sheetjs.com/.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-22363
- https://cdn.sheetjs.com
- https://cdn.sheetjs.com/advisories/CVE-2024-22363
- https://cwe.mitre.org/data/definitions/1333.html
- https://git.sheetjs.com/sheetjs/sheetjs
- https://git.sheetjs.com/sheetjs/sheetjs/src/tag/v0.20.2
