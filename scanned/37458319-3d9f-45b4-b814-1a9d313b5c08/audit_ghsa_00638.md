# [H] pym.js CSRF Vulnerability

## Summary
Severity: High
Advisory: GHSA-82gw-pqf7-q3j2
CVE: CVE-2018-1000086
CWE: CWE-352
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-03-13
Source: https://github.com/advisories/GHSA-82gw-pqf7-q3j2
Type: github-advisory

## Affected
- npm: `pym.js` — affected >=0.4.2 <1.3.2

## Details
NPR Visuals Team Pym.js version versions 0.4.2 up to 1.3.1 contains a Cross Site Request Forgery (CSRF) vulnerability in Pym.js `_onNavigateToMessage` function. 

https://github.com/nprapps/pym.js/blob/master/src/pym.js#L573 can result in Arbitrary javascript code execution. This attack appears to be exploitable if the Attacker gains full javascript access to pages with Pym.js embeds, or when user visits an attacker-crafted page. This vulnerability appears to have been fixed in versions 1.3.2 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000086
- https://github.com/nprapps/pym.js/issues/170
- https://github.com/nprapps/pym.js/commit/c3552a6cf2532664c17bd6a318fb3cf8e4cf2f97
- https://github.com/advisories/GHSA-82gw-pqf7-q3j2
- https://github.com/nprapps/pym.js
- http://blog.apps.npr.org/2018/02/15/pym-security-vulnerability.html
