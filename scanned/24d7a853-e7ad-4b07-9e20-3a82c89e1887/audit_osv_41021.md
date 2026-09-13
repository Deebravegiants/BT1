# [C] Gorse - Unauthenticated Database Dump and Restore via /api/dump and /api/restore Endpoints

## Summary
Severity: Critical
Advisory: CVE-2026-56782
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-56782
Type: osv

## Details
Gorse before 0.5.10 contains an authentication bypass vulnerability in the /api/dump and /api/restore endpoints that allows unauthenticated attackers to access protected functionality when admin_api_key is empty, which is the default configuration. Remote attackers can exfiltrate the entire database including user records, items, and feedback data containing personally identifiable information, or completely overwrite the dataset without authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56782.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56782
- https://www.vulncheck.com/advisories/gorse-unauthenticated-database-dump-and-restore-via-api-dump-and-api-restore-endpoints
- https://github.com/gorse-io/gorse/issues/1292
- https://github.com/gorse-io/gorse/pull/1293
- https://github.com/gorse-io/gorse/commit/19fdcbb309fb5b609e9cc3eb10c74885b5b27da9
- https://github.com/gorse-io/gorse
