# [H] Knex.js has a limited SQL injection vulnerability

## Summary
Severity: High
Advisory: GHSA-4jv9-3563-23j3
CVE: CVE-2016-20018
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-12-19
Source: https://github.com/advisories/GHSA-4jv9-3563-23j3
Type: github-advisory

## Affected
- npm: `knex` — affected >=0 <2.4.0

## Details
Knex Knex.js through 2.3.0 has a limited SQL injection vulnerability that can be exploited to ignore the WHERE clause of a SQL query. This vulnerability has been fixed in version 2.4.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-20018
- https://github.com/knex/knex/issues/1227
- https://github.com/knex/knex/pull/5417
- https://github.com/knex/knex/commit/e145322da92749be7749f9ade5b5f5a66d6586a4
- https://github.com/knex/knex
- https://github.com/knex/knex/releases/tag/2.4.0
- https://www.ghostccamm.com/blog/knex_sqli
