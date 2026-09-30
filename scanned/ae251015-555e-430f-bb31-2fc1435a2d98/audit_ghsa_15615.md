# [H] ejson shell parser in MongoDB Compass maybe bypassed

## Summary
Severity: High
Advisory: GHSA-jxr4-4prv-mh83
CVE: CVE-2024-6376
CWE: CWE-20, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-01
Source: https://github.com/advisories/GHSA-jxr4-4prv-mh83
Type: github-advisory

## Affected
- npm: `@mongodb-js/connection-form` — affected >=0 <1.20.1

## Details
MongoDB Compass may be susceptible to code injection due to insufficient sandbox protection settings with the usage of ejson shell parser in Compass' connection handling. This issue affects MongoDB Compass versions prior to version 1.42.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6376
- https://github.com/mongodb-js/compass/commit/b1f8050d49d66be3bc499cb317a1e1de45390e51
- https://github.com/mongodb-js/compass
- https://jira.mongodb.org/browse/COMPASS-7496
