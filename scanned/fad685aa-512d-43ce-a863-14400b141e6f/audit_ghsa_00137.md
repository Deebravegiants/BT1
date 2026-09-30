# [H] SQL Injection in query-mysql

## Summary
Severity: High
Advisory: GHSA-9mr8-6prp-gwjv
CVE: CVE-2018-3754
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-09-10
Source: https://github.com/advisories/GHSA-9mr8-6prp-gwjv
Type: github-advisory

## Affected
- npm: `query-mysql` — affected >=0

## Details
All versions of `query-mysql` are vulnerable to SQL injection due to lack of user input sanitization allows to run arbitrary SQL queries when fetching data from database.


## Recommendation

No fix is currently available for this vulnerability. It is our recommendation to not install or use this module if user input is passed into this module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3754
- https://hackerone.com/reports/311244
- https://github.com/advisories/GHSA-9mr8-6prp-gwjv
- https://www.npmjs.com/advisories/666
