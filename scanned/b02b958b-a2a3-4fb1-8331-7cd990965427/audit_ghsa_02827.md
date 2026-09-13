# [M] Denial of Service (DoS) in mongo-express

## Summary
Severity: Medium
Advisory: GHSA-m2r3-8492-vx59
CVE: CVE-2021-23372
CWE: CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-10-06
Source: https://github.com/advisories/GHSA-m2r3-8492-vx59
Type: github-advisory

## Affected
- npm: `mongo-express` — affected >=0

## Details
All versions of package mongo-express are vulnerable to Denial of Service (DoS) when exporting an empty collection as CSV, due to an unhandled exception, leading to a crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23372
- https://github.com/mongo-express/mongo-express
- https://snyk.io/vuln/SNYK-JS-MONGOEXPRESS-1085403
