# [M] Pannellum Cross-Site Scripting due to data not being sanitized for URIs or vbscript

## Summary
Severity: Medium
Advisory: GHSA-m52x-29pq-w3vv
CVE: CVE-2019-16763
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2019-11-22
Source: https://github.com/advisories/GHSA-m52x-29pq-w3vv
Type: github-advisory

## Affected
- npm: `pannellum` — affected >=2.5.0 <2.5.5

## Details
Versions of `pannellum` prior to 2.5.6 are vulnerable to Cross-Site Scripting (XSS). The package fails to sanitize URLs for data URIs, which may allow attackers to execute arbitrary code in a victim's browser. 


## Recommendation

Upgrade to version 2.5.6 or later.

## References
- https://github.com/mpetroff/pannellum/security/advisories/GHSA-m52x-29pq-w3vv
- https://nvd.nist.gov/vuln/detail/CVE-2019-16763
- https://github.com/mpetroff/pannellum/commit/cc2f3d99953de59db908e0c6efd1c2c17f7c6914
- https://github.com/advisories/GHSA-m52x-29pq-w3vv
- https://github.com/mpetroff/pannellum
- https://www.npmjs.com/advisories/1418
