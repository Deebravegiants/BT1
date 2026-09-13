# [C] Remote code execution in mongo-express

## Summary
Severity: Critical
Advisory: GHSA-hxmg-hm46-cf62
CVE: CVE-2020-24391
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-hxmg-hm46-cf62
Type: github-advisory

## Affected
- npm: `mongodb-query-parser` — affected >=0 <2.0.0

## Details
mongo-express before 1.0.0 offers support for certain advanced syntax but implements this in an unsafe way. NOTE: this may overlap CVE-2019-10769.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-24391
- https://github.com/mongodb-js/query-parser/issues/16
- https://github.com/mongo-express/mongo-express/commit/3a26b079e7821e0e209c3ee0cc2ae15ad467b91a
