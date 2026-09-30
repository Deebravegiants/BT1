# [M] Improper Input Validation in url-js

## Summary
Severity: Medium
Advisory: GHSA-rf54-44jr-q5vf
CVE: CVE-2022-25839
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-03-12
Source: https://github.com/advisories/GHSA-rf54-44jr-q5vf
Type: github-advisory

## Affected
- npm: `url-js` — affected >=0 <2.1.0

## Details
The package url-js before 2.1.0 is vulnerable to Improper Input Validation due to improper parsing, which makes it is possible for the hostname to be spoofed. http://\\\\\\\\localhost and http://localhost are the same URL. However, the hostname is not parsed as localhost, and the backslash is reflected as it is.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25839
- https://github.com/duzun/URL.js/commit/9dc9fcc99baa4cbda24403d81a589e9b0f4121d0
- https://github.com/duzun/URL.js
- https://snyk.io/vuln/SNYK-JS-URLJS-2414030
