# [C] query-parser-string is vulnerable to Prototype Pollution

## Summary
Severity: Critical
Advisory: GHSA-587p-w43q-4hjx
CVE: CVE-2025-63704
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-587p-w43q-4hjx
Type: github-advisory

## Affected
- npm: `query-string-parser` — affected 1.0.0

## Details
NPM package query-parser-string 1.0.0 is vulnerable to Prototype Pollution. The package does not properly sanitize user supplied query parameters and merges them to the newly created object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-63704
- https://github.com/victorteokw/query-string-parser/issues/3
- https://gist.github.com/6en6ar/d62f614dbb2b1032b5e45a56fe26ec8b
- https://github.com/victorteokw/query-string-parser
- https://www.npmjs.com/package/query-string-parser?activeTab=readme
