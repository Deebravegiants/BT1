# [C] ArcadeDB vulnerable to cross-database authorization bypass and unsecured newly-created databases

## Summary
Severity: Critical
Advisory: GHSA-fxc7-fm93-6q77
CVE: CVE-2026-44221
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-fxc7-fm93-6q77
Type: github-advisory

## Affected
- Maven: `com.arcadedb:arcadedb-server` — affected >=21.10.1 <26.4.2

## Details
### Impact
Authenticated users and API tokens scoped to a specific database could read, write, and mutate schema on any other database on the same server. Two distinct defects contributed: (1) ServerSecurityUser.getDatabaseUser() returned a DB user with an uninitialized fileAccessMap, which requestAccessOnFile treated as allow-all; (2) ArcadeDBServer.createDatabase() omitted factory.setSecurity(...) so any database created via POST /api/v1/server {"command":"create database X"} had its entire record-level authorization system silently disabled. In combination, record-level and database-level authorization could be bypassed by any authenticated principal.

### Patches
Upgrade to version 26.4.2

### Resources

https://github.com/ArcadeData/arcadedb/commit/04110c06315da55604ac107f71fe7182f3a3deb8

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-fxc7-fm93-6q77
- https://nvd.nist.gov/vuln/detail/CVE-2026-44221
- https://github.com/ArcadeData/arcadedb/commit/04110c06315da55604ac107f71fe7182f3a3deb8
- https://github.com/ArcadeData/arcadedb/commit/9e708f116b
- https://github.com/ArcadeData/arcadedb
