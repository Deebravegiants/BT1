# [C] ArcadeDB Gremlin Wire Protocol Authorization Bypass Cross-Database

## Summary
Severity: Critical
Advisory: CVE-2026-75853
Aliases: GHSA-c287-v325-j5jx
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75853
Type: osv

## Details
ArcadeDB's Gremlin wire-protocol plugin (com.arcadedb:arcadedb-gremlin) in versions <= 26.7.3 enforces authentication (SASL PLAIN) but performs no authorization: it never checks database access permissions (canAccessToDatabase) and never binds the authenticated principal into the engine. As a result, any valid server credential — even one provisioned for zero or one unrelated database — can read, write, and drop data in any database on the server by selecting a target database via a traversal-source alias, completely bypassing the engine's per-type/read-only/UPDATE_SCHEMA ACLs. The issue is fixed in version 26.8.1.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-c287-v325-j5jx
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75853.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75853
- https://www.vulncheck.com/advisories/arcadedb-gremlin-wire-protocol-authorization-bypass-cross-database
