# [H] WebErpMesv2 allows unauthenticated API Access

## Summary
Severity: High
Advisory: CVE-2026-22788
Aliases: GHSA-pp68-5pc2-hv7w
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-01-12
Source: https://osv.dev/vulnerability/CVE-2026-22788
Type: osv

## Details
WebErpMesv2 is a Resource Management and Manufacturing execution system Web for industry. Prior to 1.19, the WebErpMesV2 application exposes multiple sensitive API endpoints without authentication middleware. An unauthenticated remote attacker can read business-critical data including companies, quotes, orders, tasks, and whiteboards. Limited write access allows creation of company records and full manipulation of collaboration whiteboards. This vulnerability is fixed in 1.19.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22788.json
- https://github.com/SMEWebify/WebErpMesv2/security/advisories/GHSA-pp68-5pc2-hv7w
- https://nvd.nist.gov/vuln/detail/CVE-2026-22788
- https://github.com/SMEWebify/WebErpMesv2/commit/3a7ab1c95d1d1c8f7c62c84bc87b3666ecd2fa23
