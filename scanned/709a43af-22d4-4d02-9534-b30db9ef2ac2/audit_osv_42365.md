# [C] ArcadeDB before 26.7.2 Cluster Token Disclosure via GET /api/v1/server

## Summary
Severity: Critical
Advisory: CVE-2026-67343
Aliases: GHSA-46hj-24h4-j8gf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67343
Type: osv

## Details
ArcadeDB versions before 26.7.2 fail to properly redact the cluster token in the GET /api/v1/server endpoint, allowing authenticated users to retrieve the arcadedb.ha.clusterToken value in cleartext. Attackers can use the leaked token with X-ArcadeDB-Cluster-Token and X-ArcadeDB-Forwarded-User headers to impersonate root and execute administrative actions including user creation, database operations, and server shutdown.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-46hj-24h4-j8gf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67343.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-67343
- https://www.vulncheck.com/advisories/arcadedb-before-cluster-token-disclosure-via-get-api-v1-server
