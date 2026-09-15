# [H] SurrealDB memory exhaustion via string::replace using regex 

## Summary
Severity: High
Advisory: GHSA-3633-g6mg-p6qq
CWE: CWE-789
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-11
Source: https://github.com/advisories/GHSA-3633-g6mg-p6qq
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=2.2.0 <2.2.2
- crates.io: `surrealdb` — affected >=2.1.0 <2.1.5
- crates.io: `surrealdb` — affected >=0 <2.0.5

## Details
An authenticated user can craft a query using the `string::replace` function that uses a Regex to perform a string replacement. As there is a failure to restrict the resulting string length, this enables an attacker to send a `string::replace` function to the SurrealDB server exhausting all the memory of the server due to string allocations. This eventually results in a Denial-of-Service situation for the SurrealDB server.

This issue was discovered and patched during an code audit and penetration test of SurrealDB by cure53. Using CVSSv4 definitions, the severity is High. 

### Impact
An authenticated user can crash the SurrealDB instance through memory exhaustion

### Patches
A patch has been created that enforces a limit on string length  `SURREAL_GENERATION_ALLOCATION_LIMIT`

- Versions 2.0.5, 2.1.5, 2.2.2, and later are not affected by this issue

### Workarounds
Affected users who are unable to update may want to limit the ability of untrusted clients to run the `string::replace` function in the affected versions of SurrealDB using the `--deny-functions` flag described within [Capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities#functions) or the equivalent `SURREAL_CAPS_DENY_FUNC` environment variable.

### References

[SurrealQL Documentation - DB Functions (string::replace)](https://surrealdb.com/docs/surrealql/functions/database/string#stringreplace)
[SurrealDB Documentation - Capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities#functions)
[SurrealDB Documentation - Environment Variables](https://surrealdb.com/docs/surrealdb/cli/env)
[#5619 ](https://github.com/surrealdb/surrealdb/pull/5619)
[#5638 ](https://github.com/surrealdb/surrealdb/pull/5638)

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-3633-g6mg-p6qq
- https://github.com/surrealdb/surrealdb/pull/5619
- https://github.com/surrealdb/surrealdb/pull/5638
- https://github.com/surrealdb/surrealdb
