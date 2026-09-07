# [H] mysql2 vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-pmh2-wpjm-fj45
CVE: CVE-2024-21512
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2024-05-30
Source: https://github.com/advisories/GHSA-pmh2-wpjm-fj45
Type: github-advisory

## Affected
- npm: `mysql2` — affected >=0 <3.9.8

## Details
Versions of the package mysql2 before 3.9.8 are vulnerable to Prototype Pollution due to improper user input sanitization passed to fields and tables when using nestTables.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21512
- https://github.com/sidorares/node-mysql2/pull/2702
- https://github.com/sidorares/node-mysql2/commit/efe3db527a2c94a63c2d14045baba8dfefe922bc
- https://gist.github.com/domdomi3/e9f0f9b9b1ed6bfbbc0bea87c5ca1e4a
- https://github.com/sidorares/node-mysql2
- https://security.snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-7176010
- https://security.snyk.io/vuln/SNYK-JS-MYSQL2-6861580
