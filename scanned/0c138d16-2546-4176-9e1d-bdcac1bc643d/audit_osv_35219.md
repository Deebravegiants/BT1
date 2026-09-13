# [M] SQLBot uploadExcel Endpoint has Unauthenticated Arbitrary File Upload vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-69285
Aliases: GHSA-crfm-cch4-hjpv
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2025-69285
Type: osv

## Details
SQLBot is an intelligent data query system based on a large language model and RAG. Versions prior to 1.5.0 contain a missing authentication vulnerability in the /api/v1/datasource/uploadExcel endpoint, allowing a remote unauthenticated attacker to upload arbitrary Excel/CSV files and inject data directly into the PostgreSQL database. The endpoint is explicitly added to the authentication whitelist, causing the TokenMiddleware to bypass all token validation. Uploaded files are parsed by pandas and inserted into the database via to_sql() with if_exists='replace' mode. The vulnerability has been fixed in v1.5.0. No known workarounds are available.

## References
- https://github.com/dataease/SQLBot/releases/tag/v1.5.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69285.json
- https://github.com/dataease/SQLBot/security/advisories/GHSA-crfm-cch4-hjpv
- https://nvd.nist.gov/vuln/detail/CVE-2025-69285
