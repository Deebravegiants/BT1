# [M] Exposure of Resource to Wrong Sphere in valib

## Summary
Severity: Medium
Advisory: GHSA-pmpr-vc5q-h3jw
CVE: CVE-2019-10805
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-pmpr-vc5q-h3jw
Type: github-advisory

## Affected
- npm: `valib` — affected >=0

## Details
valib through 2.0.0 allows Internal Property Tampering. A maliciously crafted JavaScript object can bypass several inspection functions provided by valib. Valib uses a built-in function (hasOwnProperty) from the unsafe user-input to examine an object. It is possible for a crafted payload to overwrite this function to manipulate the inspection results to bypass security checks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10805
- https://snyk.io/vuln/SNYK-JS-VALIB-559015
- https://www.npmjs.com/package/valib
