# [M] Cross-Site Scripting in m-server

## Summary
Severity: Medium
Advisory: GHSA-gmxv-xf2q-6j8m
CVE: CVE-2018-16484
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-02-07
Source: https://github.com/advisories/GHSA-gmxv-xf2q-6j8m
Type: github-advisory

## Affected
- npm: `m-server` — affected >=0 <1.4.2

## Details
Versions of `m-server` before 1.4.2 are vulnerable to stored cross-site scripting. This vulnerability is exploitable if an attacker is able to control the name of a file that `m-server` is serving.


## Recommendation

Update to version 1.4.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16484
- https://hackerone.com/reports/319794
- https://github.com/advisories/GHSA-gmxv-xf2q-6j8m
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/467.json
- https://www.npmjs.com/advisories/729
