# [M] SurrealDB vulnerable to memory exhaustion via nested functions and scripts

## Summary
Severity: Medium
Advisory: GHSA-m7rc-8w7m-r9qr
CWE: CWE-674
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-04-10
Source: https://github.com/advisories/GHSA-m7rc-8w7m-r9qr
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=2.2.0 <2.2.2
- crates.io: `surrealdb` — affected >=2.1.0 <2.1.5
- crates.io: `surrealdb` — affected >=0 <2.0.5

## Details
In order to prevent DoS situations due to infinite recursions, SurrealDB implements a limit of nested calls for both native functions and embedded JavaScript functions.

However, in SurrealDB instances with embedded scripting functions enabled, it was found that this limit can be circumvented by utilizing both at the same time. If a native function contains JavaScript which issues a new query that calls that function, the recursion limit is not triggered.

Once executed, SurrealDB will follow the path of infinite recursions until the system runs out of memory, prior to the recursion limit being triggered.

This vulnerability can only affect SurrealDB servers explicitly enabling the scripting capability with `--allow-scripting` or 
`--allow-all` and equivalent environment variables `SURREAL_CAPS_ALLOW_SCRIPT=true` and `SURREAL_CAPS_ALLOW_ALL=true`.

This issue was discovered and patched during an code audit and penetration test of SurrealDB by cure53, the severity defined within cure53's preliminary finding is Medium, matched by our CVSS v4 assessment.

### Impact
For SurrealDB instances with embedded scripting functions enabled, this attack could be used to perform a DoS attack on the server by an authenticated user. 

### Patches
A patch has been created that further limits scripting function call limit recursion depth and disallows multiple calls to `surreadb.query()` to run in parallel in a scripting function.

- Versions 2.0.5, 2.1.5, 2.2.2 and later are not affected by this issue.

### Workarounds
Deny execution of embedded scripting functions through the configuration of [capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities#capabilities) by starting SurrealDB with the `--deny-scripting` flag or the equivalent environment variable `SURREAL_CAPS_DENY_SCRIPT=true`. This has a usability implication, although scripting functions are disabled by default.

### References
[SurrealDB Documentation - Capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities)
[SurrealQL Documentation - Scripting Functions](https://surrealdb.com/docs/surrealql/functions/script)

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-m7rc-8w7m-r9qr
- https://github.com/surrealdb/surrealdb
