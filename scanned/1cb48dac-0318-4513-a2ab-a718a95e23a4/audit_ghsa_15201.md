# [M] Uncaught Exception in surrealdb

## Summary
Severity: Medium
Advisory: GHSA-jm4v-58r5-66hj
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-18
Source: https://github.com/advisories/GHSA-jm4v-58r5-66hj
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <1.1.1

## Details
Although custom parameters and functions are only supported at the database level, it was allowed to invoke those entities at the root or namespace level. This would cause a panic which would crash the SurrealDB server, leading to denial of service.

### Impact

A client that is authorized to run queries at the root or namespace level in a SurrealDB server is able to run a query invoking a parameter or a function at that level, which will cause a panic. This will crash the server, leading to denial of service.

### Patches

- Version 1.1.1 and later are not affected by this issue.

### Workarounds

Concerned users unable to update may want to limit the ability of untrusted users to run arbitrary SurrealQL queries in the affected versions of SurrealDB to the database level. To limit the impact of the denial of service, SurrealDB administrators may also want to ensure that the SurrealDB process is running so that it can be automatically re-started after a crash.

### References

- #3297

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-jm4v-58r5-66hj
- https://github.com/surrealdb/surrealdb/commit/618a4d1b422df0d12772532bb2c195f830b40399
- https://github.com/surrealdb/surrealdb
