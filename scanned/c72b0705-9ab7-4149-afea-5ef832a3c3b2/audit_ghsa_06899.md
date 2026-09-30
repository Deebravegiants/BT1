# [H] ArcadeDB: Privilege escalation via reader role in /api/v1/command JS scripting language — arbitrary host file read

## Summary
Severity: High
Advisory: GHSA-48qw-824m-86pr
CWE: CWE-269, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-48qw-824m-86pr
Type: github-advisory

## Affected
- Maven: `com.arcadedb:arcadedb-server` — affected >=0 <26.7.1

## Details
### Impact

A user holding only `reader` (read-only) privileges on a single database could execute arbitrary JVM code by sending a `"language": "js"` command to the `POST /api/v1/command/{database}` HTTP endpoint, and use it to read arbitrary files on the host filesystem (e.g. `/etc/passwd`, configuration files), outside the scope of the database itself.

Two cooperating defects made this possible:

1. **Missing authorization on the scripting path (CWE-863 / CWE-269).** Polyglot script execution (`js` and other GraalVM languages) never went through the database authorization checks applied to SQL/Cypher, so any authenticated principal - regardless of database role - could run scripts.
2. **Sandbox whitelist bypass.** The GraalVM sandbox restricts direct class lookups to a configured `allowedPackages` list, but a script could reach arbitrary classes by reflecting off the bound `database` object: `database.getClass().getClassLoader().loadClass("java.io.File")`.

Process creation was already blocked (`allowCreateProcess(false)`), so the confirmed impact is host **file read**, not OS command execution. Confidentiality: High. Integrity/Availability: None.

This is a distinct entry point and root cause from CVE-2026-44221, CVE-2026-54076 and CVE-2026-54077, and is reproducible on builds that already contain those fixes.

### Patches

The fix is applied in the engine so it covers every entry point (HTTP command, HA-forwarded commands, MCP `analyze`), not only the HTTP handler:

- Polyglot script execution now requires the `updateSecurity` database-administrator permission on `command`, `analyze` and `registerFunctions`. The check runs on the request thread that carries the authenticated user and is a no-op in embedded mode and internal/system contexts (schema load, HA replication apply).
- The GraalVM host-access policy now denies access to `java.lang.Class`, `java.lang.ClassLoader` and `java.lang.reflect` members, closing the reflection escape that bypassed `allowedPackages` - even for authorized administrators - while leaving normal method calls on bound objects and explicit `Java.type(...)` lookups (governed by `allowedPackages`) working.

### Workarounds

Until upgraded, do not grant command/query access on the HTTP API to untrusted users, and treat any account that can reach `/api/v1/command` as capable of code execution. Note that after the fix, non-administrator accounts can no longer run `js`/polyglot scripts over HTTP.

### Credit

Reported by @kyojune76.

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-48qw-824m-86pr
- https://github.com/ArcadeData/arcadedb
- https://github.com/ArcadeData/arcadedb/releases/tag/26.7.1
