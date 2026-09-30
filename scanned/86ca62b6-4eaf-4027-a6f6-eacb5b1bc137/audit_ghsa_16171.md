# [M] SurrealDB has an Uncaught Exception in Function Generating Random Time

## Summary
Severity: Medium
Advisory: GHSA-h4f5-h82v-5w4r
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-22
Source: https://github.com/advisories/GHSA-h4f5-h82v-5w4r
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <2.1.0
- crates.io: `surrealdb-core` — affected >=0 <2.1.0

## Details
The `rand::time()` function in SurrealQL generates a random time from an optional range of two Unix timestamps. Due to the underlying use of `timestamp_opt` from the `chrono` crate, this function could potentially return `None` in some instances, leading to a panic when `unwrap` was called on its result in order to return a SurrealQL `datetime` type to the caller of the function.

### Impact

A client that is authorized to run queries in a SurrealDB server would be able to make repeated (in the order of millions) calls to `rand::time()` in order to reliably trigger a panic. This would crash the server, leading to denial of service.

### Patches

The function has been updated in to guarantee that some `datetime` is returned or that an error is otherwise gracefully handled.

- Version 2.1.0 and later are not affected by this issue.

### Workarounds

Affected users who are unable to update may want to limit the ability of untrusted clients to run the `rand::time()` function in the affected versions of SurrealDB using security capabilities. To limit the impact of the denial of service, SurrealDB administrators may also want to ensure that the SurrealDB process is running so that it can be automatically re-started after a crash.

### References

- #5126
- [SurrealQL Documentation - Database Functions (`rand::time`)](https://surrealdb.com/docs/surrealql/functions/database/rand#randtime)
- [SurrealDB Documentation - Security Capabilities (Functions)](https://surrealdb.com/docs/surrealdb/security/capabilities#functions)

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-h4f5-h82v-5w4r
- https://github.com/surrealdb/surrealdb/pull/5126
- https://github.com/surrealdb/surrealdb
