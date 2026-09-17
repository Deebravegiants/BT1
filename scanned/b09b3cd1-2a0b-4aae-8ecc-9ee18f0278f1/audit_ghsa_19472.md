# [M] http-proxy-middleware can call writeBody twice because "else if" is not used

## Summary
Severity: Medium
Advisory: GHSA-4www-5p9h-95mh
CVE: CVE-2025-32996
CWE: CWE-670
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:N/A:L (CVSS_V3)
Published: 2025-04-15
Source: https://github.com/advisories/GHSA-4www-5p9h-95mh
Type: github-advisory

## Affected
- npm: `http-proxy-middleware` — affected >=1.3.0 <2.0.8
- npm: `http-proxy-middleware` — affected >=3.0.0 <3.0.4

## Details
In http-proxy-middleware before 2.0.8 and 3.x before 3.0.4, writeBody can be called twice because "else if" is not used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-32996
- https://github.com/chimurai/http-proxy-middleware/pull/1089
- https://github.com/chimurai/http-proxy-middleware/commit/020976044d113fc0bcbbaf995e91d05e2829a145
- https://github.com/chimurai/http-proxy-middleware
- https://github.com/chimurai/http-proxy-middleware/releases/tag/v2.0.8
- https://github.com/chimurai/http-proxy-middleware/releases/tag/v3.0.4
