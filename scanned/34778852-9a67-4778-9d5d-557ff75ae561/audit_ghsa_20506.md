# [H] Server side request forgery in @isomorphic-git/cors-proxy

## Summary
Severity: High
Advisory: GHSA-v82v-rq72-phq9
CVE: CVE-2021-23664
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-01-26
Source: https://github.com/advisories/GHSA-v82v-rq72-phq9
Type: github-advisory

## Affected
- npm: `@isomorphic-git/cors-proxy` — affected >=0 <2.7.1

## Details
The package @isomorphic-git/cors-proxy before 2.7.1 is vulnerable to Server-side Request Forgery (SSRF) due to missing sanitization and validation of the redirection action in middleware.js.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23664
- https://github.com/isomorphic-git/cors-proxy/commit/1b1c91e71d946544d97ccc7cf0ac62b859e03311
- https://github.com/isomorphic-git/cors-proxy
- https://snyk.io/vuln/SNYK-JS-ISOMORPHICGITCORSPROXY-1734788
