# [M] ArcadeDB before 26.8.1 Permission Bypass via DEFINE FUNCTION

## Summary
Severity: Medium
Advisory: CVE-2026-76223
Aliases: GHSA-rv64-62hr-wv2p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-76223
Type: osv

## Details
ArcadeDB (com.arcadedb) versions 26.7.3 and earlier fail to enforce the UPDATE_SCHEMA permission check when a DEFINE FUNCTION statement targets an already-existing function library. A user with only database access can add or overwrite SQL or Cypher functions in an existing library and persist the change, enabling tampering with admin-defined function logic. The issue is fixed in 26.8.1. (JavaScript functions still trigger the UPDATE_SECURITY check and are not affected.)

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-rv64-62hr-wv2p
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/76xxx/CVE-2026-76223.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-76223
- https://www.vulncheck.com/advisories/arcadedb-before-permission-bypass-via-define-function
