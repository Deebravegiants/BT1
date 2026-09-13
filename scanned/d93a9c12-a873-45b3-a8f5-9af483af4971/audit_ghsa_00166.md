# [H] Prototype Pollution in assign-deep

## Summary
Severity: High
Advisory: GHSA-xcvv-84j5-jw9h
CVE: CVE-2018-3720
CWE: CWE-1321, CWE-471
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-xcvv-84j5-jw9h
Type: github-advisory

## Affected
- npm: `assign-deep` — affected >=0 <0.4.7

## Details
Versions of `assign-deep` before 0.4.7 are vulnerable to prototype pollution via merging functions.


## Recommendation

Update to version 0.4.7 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3720
- https://github.com/jonschlinkert/assign-deep/commit/19953a8c089b0328c470acaaaf6accdfcb34da11
- https://hackerone.com/reports/310707
- https://github.com/advisories/GHSA-xcvv-84j5-jw9h
- https://www.npmjs.com/advisories/579
