# [M] Information Exposure on Case Insensitive File Systems in serve

## Summary
Severity: Medium
Advisory: GHSA-686g-3xr3-x4x6
CVE: CVE-2018-3809
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2018-07-18
Source: https://github.com/advisories/GHSA-686g-3xr3-x4x6
Type: github-advisory

## Affected
- npm: `serve` — affected >=0 <7.0.0

## Details
Versions of `serve` before 7.0.0 are vulnerable to information exposure, bypassing the ignore security control, but only on case insensitive file systems.



## Recommendation

Update to version 7.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3809
- https://hackerone.com/reports/330650
- https://github.com/advisories/GHSA-686g-3xr3-x4x6
- https://www.npmjs.com/advisories/672
