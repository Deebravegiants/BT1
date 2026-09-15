# [C] Prototype Pollution in js-data

## Summary
Severity: Critical
Advisory: GHSA-c6h4-gc3f-hgjq
CVE: CVE-2021-23574
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-c6h4-gc3f-hgjq
Type: github-advisory

## Affected
- npm: `js-data` — affected >=0

## Details
All versions of package js-data are vulnerable to Prototype Pollution via the deepFillIn and the set functions. This is an incomplete fix of [CVE-2020-28442](https://snyk.io/vuln/SNYK-JS-JSDATA-1023655).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23574
- https://github.com/js-data/js-data/issues/576
- https://github.com/js-data/js-data/issues/577
- https://github.com/js-data/js-data
- https://github.com/js-data/js-data/blob/master/dist/js-data.js%23L472
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-2320790
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2320791
- https://snyk.io/vuln/SNYK-JS-JSDATA-1584361
