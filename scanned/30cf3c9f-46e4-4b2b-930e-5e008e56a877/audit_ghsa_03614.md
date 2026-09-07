# [M] Cross-Site Scripting in serialize-javascript

## Summary
Severity: Medium
Advisory: GHSA-h9rv-jmmf-4pgx
CVE: CVE-2019-16769
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2019-12-05
Source: https://github.com/advisories/GHSA-h9rv-jmmf-4pgx
Type: github-advisory

## Affected
- npm: `serialize-javascript` — affected >=0 <2.1.1

## Details
Versions of `serialize-javascript` prior to 2.1.1 are vulnerable to Cross-Site Scripting (XSS). The package fails to sanitize serialized regular expressions. This vulnerability does not affect Node.js applications.


## Recommendation

Upgrade to version 2.1.1 or later.

## References
- https://github.com/yahoo/serialize-javascript/security/advisories/GHSA-h9rv-jmmf-4pgx
- https://nvd.nist.gov/vuln/detail/CVE-2019-16769
- https://github.com/advisories/GHSA-h9rv-jmmf-4pgx
- https://www.npmjs.com/advisories/1426
