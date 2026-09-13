# [M] Chat2DB < 5.3.0 Insecure Direct Object Reference via GET /api/connection/datasource

## Summary
Severity: Medium
Advisory: CVE-2026-63307
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-17
Source: https://osv.dev/vulnerability/CVE-2026-63307
Type: osv

## Details
Chat2DB before 5.3.0 contains an insecure direct object reference vulnerability in the GET /api/connection/datasource/{id} endpoint. The handler calls dataSourceService.queryExistent(id, ...) without an ownership check and returns the decrypted password field, allowing any authenticated non-admin user to enumerate datasource IDs and read the plaintext database credentials of datasources owned by other users.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63307.json
- https://github.com/OtterMind/Chat2DB/releases/tag/v5.3.0
- https://nvd.nist.gov/vuln/detail/CVE-2026-63307
- https://www.vulncheck.com/advisories/forgecode-arbitrary-code-execution-via-unvetted-mcp-json-in-untrusted-repository
- https://github.com/OtterMind/Chat2DB
- https://github.com/OtterMind/Chat2DB/issues/1839
