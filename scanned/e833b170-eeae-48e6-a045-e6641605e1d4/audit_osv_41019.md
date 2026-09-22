# [C] Teable - Missing Authorization in v2 REST API

## Summary
Severity: Critical
Advisory: CVE-2026-56773
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-56773
Type: osv

## Details
Teable's v2 REST API controller lacks @Permissions metadata on ORPC endpoints, allowing any authenticated user to bypass authorization checks. Attackers can read table schemas, create tables, and modify or delete records across bases and tables via endpoints like GET /api/v2/tables/get and POST /api/v2/tables/updateRecords.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56773.json
- https://github.com/teableio/teable/releases/tag/release.2026-06-15T04-43-24Z.1912
- https://nvd.nist.gov/vuln/detail/CVE-2026-56773
- https://www.vulncheck.com/advisories/teable-missing-authorization-in-v2-rest-api
- https://github.com/teableio/teable/pull/3285
- https://github.com/teableio/teable
