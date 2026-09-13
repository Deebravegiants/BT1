# [H] ArcadeDB: Read-only users can mutate database schema (incomplete fix of CVE-2026-44221)

## Summary
Severity: High
Advisory: GHSA-vg6x-6pg9-6qwg
CVE: CVE-2026-54076
CWE: CWE-862, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-vg6x-6pg9-6qwg
Type: github-advisory

## Affected
- Maven: `com.arcadedb:arcadedb-engine` — affected >=0 <26.6.1

## Details
### Impact

The fix for CVE-2026-44221 (GHSA-fxc7-fm93-6q77) added an `UPDATE_SCHEMA` authorization check to a single schema-mutating method (`LocalDocumentType.createProperty`). The remaining public schema mutators were left unchecked, so an authenticated identity (including a **read-only API token**) that lacks the `UPDATE_SCHEMA` permission could still mutate the database schema on its own database:

- `DROP PROPERTY <type>.<property>`
- `ALTER TYPE <name> SUPERTYPE +<other>` / `-<other>` (change the inheritance hierarchy)
- `ALTER TYPE <name> NAME <newName>` (rename a type)
- type alias and bucket changes
- `ALTER PROPERTY <type>.<property> ...` (MANDATORY, READONLY, NOTNULL, MIN, MAX, REGEXP, DEFAULT, OF, CUSTOM) — the `LocalProperty` setters had no check at all

This does not directly disclose or write record data, but it corrupts the meaning of every stored record and breaches the documented permission model, which advertises `UPDATE_SCHEMA` as the gating right for schema mutation.

### Affected component

Engine schema layer: `engine/src/main/java/com/arcadedb/schema/LocalDocumentType.java` and `engine/src/main/java/com/arcadedb/schema/LocalProperty.java`, reachable via the SQL `DROP PROPERTY`, `ALTER TYPE`, and `ALTER PROPERTY` statements over the database command/query HTTP endpoints.

### Patches

Every public schema-mutating method on `LocalDocumentType` and `LocalProperty` now enforces `checkPermissionsOnDatabase(UPDATE_SCHEMA)` via a shared helper. The check is a no-op in embedded mode and in system contexts with no bound user (schema load at startup, HA replication apply), so internal paths and administrators are unaffected.

### Workarounds

Grant write access only to trusted users and API tokens; treat all schema DDL as administrator-only at the application layer until upgraded.

### Resources

Incomplete-fix sibling of CVE-2026-44221 / GHSA-fxc7-fm93-6q77.

### Credit

Reported by Kai Aizen (SnailSploit).

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-vg6x-6pg9-6qwg
- https://github.com/ArcadeData/arcadedb
- https://github.com/ArcadeData/arcadedb/releases/tag/26.6.1
