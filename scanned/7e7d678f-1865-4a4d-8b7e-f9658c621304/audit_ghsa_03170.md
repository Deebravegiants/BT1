# [H] Regular expression denial of service in npm-user-validate

## Summary
Severity: High
Advisory: GHSA-pw54-mh39-w3hc
CVE: CVE-2020-7754
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-pw54-mh39-w3hc
Type: github-advisory

## Affected
- npm: `npm-user-validate` — affected >=0 <1.0.1

## Details
This affects the package npm-user-validate before 1.0.1. The regex that validates user emails took exponentially longer to process long input strings beginning with @ characters.

## References
- https://github.com/npm/npm-user-validate/security/advisories/GHSA-xgh6-85xh-479p
- https://nvd.nist.gov/vuln/detail/CVE-2020-7754
- https://github.com/npm/npm-user-validate/commit/c8a87dac1a4cc6988b5418f30411a8669bef204e
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1019353
- https://snyk.io/vuln/SNYK-JS-NPMUSERVALIDATE-1019352
