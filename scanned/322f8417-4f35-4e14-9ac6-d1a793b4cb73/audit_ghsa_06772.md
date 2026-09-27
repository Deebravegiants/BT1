# [M] SurrealDB: Authorization Bypass in KILL Statement Allows Termination of Other Users' Live Queries

## Summary
Severity: Medium
Advisory: GHSA-gcwr-5mrf-fvch
CWE: CWE-862
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-gcwr-5mrf-fvch
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
The `KILL` statement is used to terminate `LIVE SELECT` subscriptions that capture real-time changes to data within a table. The `KILL` statement implementation in `core/src/expr/statements/kill.rs` verifies that the requesting user has database-level access, but does not verify that the requesting user is the owner of the live query being terminated.
 
After passing the `valid_for_db()` check, the `KILL` statement resolves the live query UUID, looks up the corresponding live query entry, and immediately deletes it without comparing the requesting user's identity against the live query owner. This allows any authenticated user with database-level access to terminate any live query in that database, regardless of who created it.
 
The affected user's real-time subscription silently stops receiving updates with no notification that the live query was terminated. The same attack works across privilege levels: a low-privilege record-scoped user can terminate a root user's monitoring live queries.
 
This issue was discovered and patched during a code audit and penetration test of SurrealDB by cure53, the severity defined within cure53's preliminary finding is Medium, matched by our CVSS v3.1 assessment.
 
### Impact
 
An authenticated user with database-level access can terminate any other user's live query subscriptions within the same database by issuing a `KILL` statement with the target live query's UUID. This impacts availability by silently disrupting real-time data subscriptions and breaks multi-tenant isolation guarantees.
 
The attack requires knowledge of the target live query UUID. Live query UUIDs are randomly generated, but may be exposed through application logs, shared monitoring dashboards, or other information disclosure vectors.
 
### Patches
 
An ownership verification check has been introduced in the `KILL` statement implementation that compares the requesting user's authentication context against the owner of the live query before allowing deletion.
 
- Versions 3.1.0 and later are not affected by this issue.
 
### Workarounds
 
Users unable to upgrade should consider the following mitigations:
 
- Ensure that live query UUIDs are treated as sensitive values and are not exposed to other users through application logs, error messages, or shared interfaces.
- Where multi-tenant isolation is critical, use separate databases per tenant rather than relying on record-level access controls within a shared database.
- Monitor for unexpected termination of live queries in application logic and implement reconnection and re-subscription mechanisms.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-gcwr-5mrf-fvch
- https://github.com/surrealdb/surrealdb/commit/36f0a41a69b551172c7d1d13b1e8dbbd868e2ead
- https://github.com/surrealdb/surrealdb
