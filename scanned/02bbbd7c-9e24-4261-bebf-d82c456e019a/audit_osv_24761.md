# [H] CVE-2023-26132

## Summary
Severity: High
Advisory: CVE-2023-26132
Aliases: GHSA-4gxf-g5gf-22h4
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H/E:P)
Published: 2023-06-10
Source: https://osv.dev/vulnerability/CVE-2023-26132
Type: osv

## Details
Versions of the package dottie before 2.0.4 are vulnerable to Prototype Pollution due to insufficient checks, via the set() function and the current variable in the /dottie.js file.

## References
- https://github.com/mickhansen/dottie.js/blob/b48e22714aae4489ea6276452f22cc61980ba5a4/dottie.js%23L107
- https://security.snyk.io/vuln/SNYK-JS-DOTTIE-3332763
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/26xxx/CVE-2023-26132.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-26132
- https://github.com/mickhansen/dottie.js/commit/7d3aee1c9c3c842720506e131de7e181e5c8db68
