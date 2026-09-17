# [H] Prototype Pollution in merge-deep

## Summary
Severity: High
Advisory: GHSA-9g9w-hmvj-5h57
CVE: CVE-2018-3722
CWE: CWE-471
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-9g9w-hmvj-5h57
Type: github-advisory

## Affected
- npm: `merge-deep` — affected >=0 <3.0.1

## Details
Versions of `merge-deep` before 3.0.1 are vulnerable to prototype pollution via merging functions.


## Recommendation

Update to version 3.0.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3722
- https://github.com/jonschlinkert/merge-deep/commit/2c33634da7129a5aefcc262d2fec2e72224404e5
- https://hackerone.com/reports/310708
- https://github.com/advisories/GHSA-9g9w-hmvj-5h57
- https://www.npmjs.com/advisories/580
