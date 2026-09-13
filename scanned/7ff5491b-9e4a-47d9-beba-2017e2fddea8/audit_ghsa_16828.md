# [C] MySQL2 for Node Arbitrary Code Injection

## Summary
Severity: Critical
Advisory: GHSA-4rch-2fh8-94vw
CVE: CVE-2024-21511
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-23
Source: https://github.com/advisories/GHSA-4rch-2fh8-94vw
Type: github-advisory

## Affected
- npm: `mysql2` — affected >=0 <3.9.7

## Details
Versions of the package mysql2 before 3.9.7 are vulnerable to Arbitrary Code Injection due to improper sanitization of the timezone parameter in the readCodeFor function by calling a native MySQL Server date/time function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21511
- https://github.com/sidorares/node-mysql2/pull/2608
- https://github.com/sidorares/node-mysql2/commit/7d4b098c7e29d5a6cb9eac2633bfcc2f0f1db713
- https://github.com/sidorares/node-mysql2
- https://github.com/sidorares/node-mysql2/releases/tag/v3.9.7
- https://security.snyk.io/vuln/SNYK-JS-MYSQL2-6670046
