# [H] ArcadeDB: Scripting authorization gate (GHSA-48qw-824m-86pr) bypassed via SQL DEFINE FUNCTION ... LANGUAGE js

## Summary
Severity: High
Advisory: GHSA-vwjc-v7x7-cm6g
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-16
Source: https://github.com/advisories/GHSA-vwjc-v7x7-cm6g
Type: github-advisory

## Affected
- Maven: `com.arcadedb:arcadedb-engine` — affected >=0 <26.7.2

## Details
The GHSA-48qw-824m-86pr hardening added a checkPermissionsOnDatabase(UPDATE_SECURITY) gate on the polyglot engine (PolyglotQueryEngine.java:112-114,126,176,199), but only there. The SQL route to JavaScript never touches it: DefineFunctionStatement.executeSimple (DefineFunctionStatement.java:37-100), LocalSchema.registerFunctionLibrary, and SQLQueryEngine library-function invocation (SQLQueryEngine.java:198-224) do no scripting-permission check.

Exploit: any user authorized for the DB (including a read-only role) runs POST /api/v1/command/<db> {"language":"sql","command":"DEFINE FUNCTION x.run \"<js>\" LANGUAGE js"} then SELECT x.run(), executing arbitrary JavaScript and defeating the control meant to restrict scripting to security admins. On this path allowedPackages is empty so Java.type host lookup and reflection are blocked, but IOAccess.ALL still permits load(url) SSRF/remote-JS inclusion and unbounded CPU/memory DoS.

Fix: gate DefineFunctionStatement.executeSimple, the SQLQueryEngine library-function wrapper (to also cover pre-existing libraries), and DeleteFunctionStatement with UPDATE_SECURITY for js/polyglot languages. Centralize as one assertCanExecuteUserCode(database) invoked by every code-execution surface. Also set IOAccess.NONE / PolyglotAccess.NONE on the Context (GraalPolyglotEngine.java:86,91).

## References
- https://github.com/ArcadeData/arcadedb/security/advisories/GHSA-vwjc-v7x7-cm6g
- https://github.com/ArcadeData/arcadedb
- https://github.com/ArcadeData/arcadedb/releases/tag/26.7.2
