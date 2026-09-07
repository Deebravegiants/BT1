# [H] ejs vulnerable to DoS due to weak input validation

## Summary
Severity: High
Advisory: GHSA-6x77-rpqf-j6mw
CVE: CVE-2017-1000189
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2018-03-05
Source: https://github.com/advisories/GHSA-6x77-rpqf-j6mw
Type: github-advisory

## Affected
- npm: `ejs` — affected >=0 <2.5.5

## Details
nodejs ejs version older than 2.5.5 is vulnerable to a denial-of-service due to weak input validation in `ejs.renderFile()`

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000189
- https://github.com/mde/ejs/commit/49264e0037e313a0a3e033450b5c184112516d8f
- https://github.com/advisories/GHSA-6x77-rpqf-j6mw
- https://github.com/mde/ejs
- https://web.archive.org/web/20171123041449/http://www.securityfocus.com/bid/101893
