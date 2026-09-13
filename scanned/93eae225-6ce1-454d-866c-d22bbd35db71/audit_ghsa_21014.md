# [C] steal vulnerable to Prototype Pollution via requestedVersion variable

## Summary
Severity: Critical
Advisory: GHSA-93q5-3xpc-8vg3
CVE: CVE-2022-37257
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-93q5-3xpc-8vg3
Type: github-advisory

## Affected
- npm: `steal` — affected >=0

## Details
Prototype pollution vulnerability in function convertLater in npm-convert.js in stealjs steal via the requestedVersion variable in the npm-convert.js file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37257
- https://github.com/stealjs/steal/issues/1526
- https://github.com/stealjs/steal
- https://github.com/stealjs/steal/blob/c9dd1eb19ed3f97aeb93cf9dcea5d68ad5d0ced9/ext/npm-convert.js#L362
- https://github.com/stealjs/steal/blob/c9dd1eb19ed3f97aeb93cf9dcea5d68ad5d0ced9/ext/npm-convert.js#L371
