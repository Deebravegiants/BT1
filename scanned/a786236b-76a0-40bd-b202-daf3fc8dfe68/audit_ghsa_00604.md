# [M] Stored Cross-Site Scripting in tianma-static

## Summary
Severity: Medium
Advisory: GHSA-jhgp-hvj6-x2p2
CVE: CVE-2018-16474
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-06
Source: https://github.com/advisories/GHSA-jhgp-hvj6-x2p2
Type: github-advisory

## Affected
- npm: `tianma-static` — affected >=0

## Details
All versions of `tianma-static` are vulnerable to stored cross-site scripting (XSS). The vulnerability is exploitable if a user can control the name of a file that is served by `tianma-static`


## Recommendation

As no fix is available for this vulnerability at this time it is our recommendation to use another static file server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16474
- https://hackerone.com/reports/403692
- https://github.com/advisories/GHSA-jhgp-hvj6-x2p2
- https://www.npmjs.com/advisories/741
