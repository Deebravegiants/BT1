# [H] Infinite loop in jpeg-js

## Summary
Severity: High
Advisory: GHSA-xvf7-4v9q-58w6
CVE: CVE-2022-25851
CWE: CWE-835
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-11
Source: https://github.com/advisories/GHSA-xvf7-4v9q-58w6
Type: github-advisory

## Affected
- npm: `jpeg-js` — affected >=0 <0.4.4

## Details
The package jpeg-js before 0.4.4 is vulnerable to Denial of Service (DoS) where a particular piece of input will cause the program to enter an infinite loop and never return.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25851
- https://github.com/jpeg-js/jpeg-js/issues/105
- https://github.com/jpeg-js/jpeg-js/pull/106
- https://github.com/jpeg-js/jpeg-js/commit/9ccd35fb5f55a6c4f1902ac5b0f270f675750c27
- https://github.com/jpeg-js/jpeg-js
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2860295
- https://snyk.io/vuln/SNYK-JS-JPEGJS-2859218
