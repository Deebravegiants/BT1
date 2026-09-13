# [H] SurrealDB CPU exhaustion via custom functions result in total DoS

## Summary
Severity: High
Advisory: GHSA-pxw4-94j3-v9pf
CWE: CWE-835
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-11
Source: https://github.com/advisories/GHSA-pxw4-94j3-v9pf
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=2.2.0 <2.2.2
- crates.io: `surrealdb` — affected >=2.1.0 <2.1.5
- crates.io: `surrealdb` — affected >=0 <2.0.5

## Details
SurrealDB allows authenticated users with `OWNER` or `EDITOR` permissions at the root, database or namespace levels to define their own database functions using the `DEFINE FUNCTION` statement

A custom database function comprises a name together with a function body. In the function body, the user programs the functionality of the function in terms of SurrealQL. The language includes a `FOR` keyword, used to implement for-loops.

Whilst the parser and interpreter constrain the number of iterations for a single for-loop, nesting several for-loops with a large number of iterations is possible. Thus, an attacker could define a function that comprises several nested for-loops with an iteration count of 1.000.000 each. 

Executing the function will consume all the CPU time of the server, timeouts configured will not break the CPU consumption, and the function execution monopolizes all CPU time of the SurrealDB server, effectively preventing the server from executing functions, queries, commands of other users, or allowing further connections being established to the server.

Terminating the stuck server requires manual intervention which forces a quit on the server process, as the server application is not responsive any longer.

This issue was discovered and patched during an code audit and penetration test of SurrealDB by cure53, the severity defined within cure53's preliminary finding is high, matched by our CVSS v4 assessment.

### Impact
Denial of Service vulnerability resulting in a stuck SurrealDB server requiring manual restart.

### Patches
A patch has been introduced that adds a check in the `ForEachStatement` that checks if the context has been cancelled or timed out for every iteration.

- Versions 2.0.5, 2.1.5, 2.2.2, and later are not affected by this issue.

### Workarounds
For SurrealDB users that are unable to upgrade, consider setting the `--allow-functions` and/or `--deny-functions` options or corresponding `SURREAL_CAPS_ALLOW_FUNC` and/or `SURREAL_CAPS_DENY_FUNC` environment variables, documented within [capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities#functions), to either block all custom functions, or only allow trusted functions to execute. 


### References
[SurrealQL Documentation - DEFINE FUNCTION Statement](https://surrealdb.com/docs/surrealql/statements/define/function)
[SurrealQL Documentation - FOR Statement](https://surrealdb.com/docs/surrealql/statements/for)
[SurrealDB Documentation - Capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities#functions)
[SurrealDB Documentation - Environment variables](https://surrealdb.com/docs/surrealdb/cli/env#command-environment-variables)
[#5597](https://github.com/surrealdb/surrealdb/pull/5597)

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-pxw4-94j3-v9pf
- https://github.com/surrealdb/surrealdb/pull/5597
- https://github.com/surrealdb/surrealdb
