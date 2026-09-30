# [M] Ghostfolio - Unauthorized Portfolio Data Exposure via Public Endpoint

## Summary
Severity: Medium
Advisory: CVE-2026-59708
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-59708
Type: osv

## Details
The GET /api/v1/public/:accessId/portfolio endpoint in ghostfolio accepts private access IDs without validating granteeUserId filtering, allowing unauthenticated access to full portfolio data. Attackers with a private access ID can retrieve sensitive portfolio information including holdings, quantities, buy prices, and performance metrics without authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59708.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-59708
- https://www.vulncheck.com/advisories/ghostfolio-unauthorized-portfolio-data-exposure-via-public-endpoint
- https://github.com/ghostfolio/ghostfolio/issues/7197
- https://github.com/ghostfolio/ghostfolio/commit/697ef59e3b58bebc5c21a9e482e4f5643390f316
- https://github.com/ghostfolio/ghostfolio
