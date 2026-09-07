# [M] Open Redirect in hekto

## Summary
Severity: Medium
Advisory: GHSA-qmm9-x5gr-4gfm
CVE: CVE-2018-3743
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-07-18
Source: https://github.com/advisories/GHSA-qmm9-x5gr-4gfm
Type: github-advisory

## Affected
- npm: `hekto` — affected >=0 <0.2.4

## Details
Versions of `hekto` before 0.2.4 are vulnerable to open redirect when a domain name is used as part of the `.html` filename.


## Recommendation

Update to version 0.2.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3743
- https://github.com/herber/hekto/pull/3
- https://github.com/herber/hekto/commit/1e5c75f8259ba0daf9b2600db3c246cda1934c46
- https://hackerone.com/reports/320693
- https://github.com/advisories/GHSA-qmm9-x5gr-4gfm
- https://www.npmjs.com/advisories/669
