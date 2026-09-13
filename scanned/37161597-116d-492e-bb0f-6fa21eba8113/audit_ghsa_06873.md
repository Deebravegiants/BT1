# [H] ArcadeDB: Trigger scripts run with java.lang.* allowed, enabling OS command execution (RCE)

## Summary
Severity: High
Advisory: GHSA-x9f9-r4m8-9xc2
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-x9f9-r4m8-9xc2
Type: github-advisory

## Affected
- Maven: `com.arcadedb:arcadedb-engine` — affected >=0 <26.7.2

## Details
ScriptTriggerExecutor sets allowedPackages to java.lang.*, java.util.*, java.time.*, java.math.* (ScriptTriggerExecutor.java:56); trigger creation is gated only at UPDATE_SCHEMA (LocalSchema.createTrigger:636). Permitting java.lang.* host-class lookup lets a trigger script do Java.type("java.lang.Runtime").getRuntime().exec(...) (or ProcessBuilder). The reflection denylist does not block Java.type host lookups, and allowCreateProcess(false) only restricts GraalVM's guest process API, not a host Runtime.exec reached through HostAccess.ALL.

Exploit: a user with UPDATE_SCHEMA (schema admin, strictly less than security admin) runs CREATE TRIGGER ... EXECUTE JAVASCRIPT '<runtime.exec>' and obtains OS RCE when the trigger fires.

Fix: remove java.lang.* (and narrow the rest) from the trigger allow-list; if host interop is needed, expose an explicit @HostAccess.Export API surface instead of whole packages; consider gating trigger creation at UPDATE_SECURITY. Prefer an allow-list (HostAccess.EXPLICIT) over the current denylist-over-HostAccess.ALL.

Related medium/low items to fold into the fix: IMPORT DATABASE SSRF via unfollowed-redirect re-validation (SourceDiscovery.java:113), BACKUP/EXPORT DATABASE missing authorization (BackupDatabaseStatement.java:56, ExportDatabaseStatement.java:52), chunked-transfer body-size DoS bypass (HttpServer.java:301,318-333), and no brute-force lockout on password auth (ServerSecurity.java:189-205).

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-x9f9-r4m8-9xc2
- https://github.com/ArcadeData/arcadedb
- https://github.com/ArcadeData/arcadedb/releases/tag/26.7.2
