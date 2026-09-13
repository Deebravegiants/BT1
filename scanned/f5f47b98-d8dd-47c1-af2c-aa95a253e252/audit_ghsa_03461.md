# [M] Regular Expression Denial of Service (ReDoS) in es6-crawler-detect

## Summary
Severity: Medium
Advisory: GHSA-jxg6-fhwc-9v9c
CVE: CVE-2020-28501
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-jxg6-fhwc-9v9c
Type: github-advisory

## Affected
- npm: `es6-crawler-detect` — affected >=0 <3.1.3

## Details
This affects the package es6-crawler-detect before 3.1.3. No limitation of user agent string length supplied to regex operators.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28501
- https://github.com/JefferyHus/es6-crawler-detect/pull/27
- https://snyk.io/vuln/SNYK-JS-ES6CRAWLERDETECT-1051529
