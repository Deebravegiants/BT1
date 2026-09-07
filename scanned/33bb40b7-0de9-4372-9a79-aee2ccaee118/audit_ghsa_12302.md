# [M] Cross Site Scripting (XSS) in plotly.js

## Summary
Severity: Medium
Advisory: GHSA-2fqv-h3r5-m4vf
CVE: CVE-2017-1000006
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-2fqv-h3r5-m4vf
Type: github-advisory

## Affected
- npm: `plotly.js` — affected >=0 <1.16.0

## Details
Affected versions of `plotly.js` are vulnerable to cross-site scripting if an attacker can convince a user to visit a malicious plot on a site using this package.


## Recommendation

Update to 1.16.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000006
- https://acloudtree.com/2016-08-09-how-i-hacked-plotly-by-exploiting-a-svg-vulnerability-in-plotlyjs
- https://github.com/advisories/GHSA-2fqv-h3r5-m4vf
- https://www.npmjs.com/advisories/145
- http://help.plot.ly/security-advisories/2016-08-08-plotlyjs-xss-advisory
