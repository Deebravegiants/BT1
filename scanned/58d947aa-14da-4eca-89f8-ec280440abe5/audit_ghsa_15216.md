# [M] Uncontrolled Recursion in SurrealQL Parsing

## Summary
Severity: Medium
Advisory: GHSA-6r8p-hpg7-825g
CWE: CWE-674
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-18
Source: https://github.com/advisories/GHSA-6r8p-hpg7-825g
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <1.1.0

## Details
In some specific instances, the SurrealQL parser will attempt to recursively parse nested statements or idioms (i.e. nested `IF` and `RELATE` statements, nested basic idioms and nested access to attributes) without checking if the depth limit established by default or in the `SURREAL_MAX_COMPUTATION_DEPTH` environment variable is exceeded. This can lead to the stack overflowing when the nesting surpasses certain levels of depth.

### Impact

An attacker that is authorized to run queries on a SurrealDB server may be able to run a query using the affected statements and idioms with very deep nesting in order to crash the server, leading to denial of service.

### Patches

- Version 1.1.0 and later are not affected by this issue.

### Workarounds

Concerned users unable to update may want to limit the ability of untrusted users to run arbitrary SurrealQL queries in the affected versions of SurrealDB. To limit the impact of the denial of service, SurrealDB administrators may also want to ensure that the SurrealDB process is running so that it can be automatically re-started after a crash.

### References

- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=62410
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=62652
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=63797
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=64445
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=64731
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=65277

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-6r8p-hpg7-825g
- https://github.com/surrealdb/surrealdb/pull/3232
- https://github.com/surrealdb/surrealdb/commit/f838da248e3854e4250e5187a3a67507cb7efaaa
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=62410
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=62652
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=63797
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=64445
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=64731
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=65277
- https://github.com/surrealdb/surrealdb
