# [C] ejs is vulnerable to remote code execution due to weak input validation

## Summary
Severity: Critical
Advisory: GHSA-3w5v-p54c-f74x
CVE: CVE-2017-1000228
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2017-11-30
Source: https://github.com/advisories/GHSA-3w5v-p54c-f74x
Type: github-advisory

## Affected
- npm: `ejs` — affected >=0 <2.5.5

## Details
nodejs ejs versions older than 2.5.3 is vulnerable to remote code execution due to weak input validation in `ejs.renderFile()` function

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000228
- https://github.com/advisories/GHSA-3w5v-p54c-f74x
- https://snyk.io/vuln/npm:ejs:20161128
- https://web.archive.org/web/20171123041219/http://www.securityfocus.com/bid/101897
