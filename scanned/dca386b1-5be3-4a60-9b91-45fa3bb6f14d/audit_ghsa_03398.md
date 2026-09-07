# [M] Cross-site scripting in SocksJS-node

## Summary
Severity: Medium
Advisory: GHSA-hh8v-jmh3-9437
CVE: CVE-2020-8823
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-hh8v-jmh3-9437
Type: github-advisory

## Affected
- npm: `sockjs` — affected >=0 <0.3.0

## Details
htmlfile in lib/transport/htmlfile.js in SockJS before 0.3.0 is vulnerable to Reflected XSS via the /htmlfile c (aka callback) parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8823
- https://github.com/theyiyibest/Reflected-XSS-on-SockJS/issues/1
- https://github.com/theyiyibest/Reflected-XSS-on-SockJS
- https://snyk.io/vuln/SNYK-JS-SOCKJS-548397
- https://www.npmjs.com/package/sockjs
- https://www.sockjs.org
