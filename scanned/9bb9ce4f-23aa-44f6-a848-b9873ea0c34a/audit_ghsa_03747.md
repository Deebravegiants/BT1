# [M] Denial of Service in rgb2hex

## Summary
Severity: Medium
Advisory: GHSA-65p8-3hm4-h9h8
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-08-23
Source: https://github.com/advisories/GHSA-65p8-3hm4-h9h8
Type: github-advisory

## Affected
- npm: `rgb2hex` — affected >=0 <0.1.6

## Details
All versions of `rgb2hex` are vulnerable to Regular Expression Denial of Service (ReDoS) when an attacker can pass in a specially crafted invalid color value.


## Recommendation

Update to version 0.1.6 or later.

## References
- https://hackerone.com/reports/319629
- https://github.com/christian-bromann/rgb2hex/blob/v0.1.0/index.js#L25
- https://snyk.io/vuln/npm:rgb2hex:20180429
- https://www.npmjs.com/advisories/647
