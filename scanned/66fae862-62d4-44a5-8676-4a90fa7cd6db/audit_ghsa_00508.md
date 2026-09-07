# [M] Cross-Site Scripting in sexstatic

## Summary
Severity: Medium
Advisory: GHSA-qfh2-6f7q-gr86
CVE: CVE-2018-3755
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-10-01
Source: https://github.com/advisories/GHSA-qfh2-6f7q-gr86
Type: github-advisory

## Affected
- npm: `sexstatic` — affected >=0

## Details
All versions of `sexstatic` are vulnerable to stored cross-site scripting (xss). This is exploitable if an attacker can control a filename that is served by `sexstatic`.



## Recommendation

As there is no fix is currently available for this vulnerability it is our recommendation to not install or used this module at this time.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3755
- https://hackerone.com/reports/328210
- https://github.com/advisories/GHSA-qfh2-6f7q-gr86
- https://www.npmjs.com/advisories/671
