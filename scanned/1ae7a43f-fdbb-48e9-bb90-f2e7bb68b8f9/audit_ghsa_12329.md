# [M] mde ejs vulnerable to XSS

## Summary
Severity: Medium
Advisory: GHSA-hwcf-pp87-7x6p
CVE: CVE-2017-1000188
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2017-11-30
Source: https://github.com/advisories/GHSA-hwcf-pp87-7x6p
Type: github-advisory

## Affected
- npm: `ejs` — affected >=0 <2.5.5

## Details
nodejs ejs version older than 2.5.5 is vulnerable to a Cross-site-scripting in the `ejs.renderFile()` resulting in code injection

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000188
- https://github.com/mde/ejs/commit/49264e0037e313a0a3e033450b5c184112516d8f
- https://github.com/advisories/GHSA-hwcf-pp87-7x6p
- https://github.com/mde/ejs
- https://web.archive.org/web/20200227134555/http://www.securityfocus.com/bid/101889
