# [H] Regular Expression Denial of Service in validator

## Summary
Severity: High
Advisory: GHSA-f5w6-r7rg-mcgq
CVE: CVE-2014-8882
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-f5w6-r7rg-mcgq
Type: github-advisory

## Affected
- npm: `validator` — affected >=0 <3.22.1

## Details
Versions of `validator` prior to 3.22.1 are affected by a regular expression denial of service vulnerability in the `isURL` method.


## Recommendation

Update to version 3.22.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-8882
- https://github.com/chriso/validator.js/issues/152#issuecomment-48107184
- https://github.com/chriso/validator.js
- https://snyk.io/vuln/npm:validator:20130705
- https://www.npmjs.com/advisories/42
