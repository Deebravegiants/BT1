# [H] Prototype Pollution in mixin-deep

## Summary
Severity: High
Advisory: GHSA-3mpr-hq3p-49h9
CVE: CVE-2018-3719
CWE: CWE-20, CWE-471
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-3mpr-hq3p-49h9
Type: github-advisory

## Affected
- npm: `mixin-deep` — affected >=0 <1.3.1

## Details
Versions of `mixin-deep` before 1.3.1 are vulnerable to prototype pollution via merging functions.


## Recommendation

Update to version 1.3.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3719
- https://github.com/jonschlinkert/mixin-deep/commit/578b0bc5e74e14de9ef4975f504dc698796bdf9c
- https://hackerone.com/reports/311236
- https://github.com/advisories/GHSA-3mpr-hq3p-49h9
- https://www.npmjs.com/advisories/578
