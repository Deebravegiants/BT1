# [H] ArcadeDB: IMPORT DATABASE allows SSRF and arbitrary local file read by authenticated users

## Summary
Severity: High
Advisory: GHSA-8w86-m9h8-hvqg
CVE: CVE-2026-54077
CWE: CWE-22, CWE-776, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-8w86-m9h8-hvqg
Type: github-advisory

## Affected
- Maven: `com.arcadedb:arcadedb-engine` — affected >=0 <26.6.1

## Details
### Impact

The SQL `IMPORT DATABASE` statement did not require administrative privileges and passed its source URL to the importer without validation. Any authenticated user with SQL command access (not only `root`/administrators) could therefore:

- **Server-Side Request Forgery (CWE-918):** cause the server to issue HTTP(S) requests to arbitrary destinations, including cloud metadata endpoints (e.g. `169.254.169.254`) and internal-only services, and ingest the responses as queryable records.
- **Arbitrary local file read (CWE-22):** read local files reachable by the server process (e.g. `/etc/passwd`, credential files) by importing `file://` paths, exposing their contents as records.

The server administration endpoint (`/api/v1/server`) was already restricted to the `root` user and was **not** affected; the exposure was through the database SQL command/query endpoints (`/api/v1/command`, `/api/v1/query`).

A related lower-severity hardening gap (CWE-776): the XML importer did not disable DTD processing, leaving entity-expansion (Billion Laughs) possible.

### Affected component

`integration/src/main/java/com/arcadedb/integration/importer/SourceDiscovery.java` (no host allow-list for http(s); no path validation for `file://`), reached from `engine/.../query/sql/parser/ImportDatabaseStatement.java`.

### Patches

- `IMPORT DATABASE` now requires the administrative `updateSecurity` permission (no-op in embedded mode).
- Import sources are validated in `SourceDiscovery`: HTTP(S) hosts resolving to loopback / link-local / private (site-local) / wildcard / multicast addresses are blocked by default (`arcadedb.server.security.importBlockLocalNetworks`, default `true`), and an optional local-path allow-list (`arcadedb.server.security.importAllowedLocalPaths`) restricts `file://` reads.
- The XML importer now disables DTD processing and external entities.

Fixed in commit referenced by pull request [#4422](https://github.com/ArcadeData/arcadedb/pull/4422).

### Workarounds

Restrict SQL command/query access to trusted administrative users; do not grant query access to untrusted users on servers that can reach sensitive networks or hold sensitive local files. Upgrading is strongly recommended.

### Credit

Reported by Bin Luo (luob87709@gmail.com).

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-8w86-m9h8-hvqg
- https://github.com/ArcadeData/arcadedb
- https://github.com/ArcadeData/arcadedb/releases/tag/26.6.1
