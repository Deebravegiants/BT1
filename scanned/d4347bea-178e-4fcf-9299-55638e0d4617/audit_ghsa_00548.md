# [C] Out-of-bounds Read in atob

## Summary
Severity: Critical
Advisory: GHSA-8w4h-3cm3-2pm2
CVE: CVE-2018-3745
CWE: CWE-125
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2018-10-09
Source: https://github.com/advisories/GHSA-8w4h-3cm3-2pm2
Type: github-advisory

## Affected
- npm: `atob` — affected >=0 <2.1.0

## Details
Versions of `atob` before 2.1.0  uninitialized Buffers when number is passed in input on Node.js 4.x and below.


## Recommendation

Update to version 2.1.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3745
- https://hackerone.com/reports/321686
- https://github.com/advisories/GHSA-8w4h-3cm3-2pm2
- https://security.netapp.com/advisory/ntap-20230622-0009
- https://www.npmjs.com/advisories/646
