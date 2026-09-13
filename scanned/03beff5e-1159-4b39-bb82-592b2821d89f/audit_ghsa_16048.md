# [M] SurrealDB has an Uncaught Exception Sorting Tables by Random Order

## Summary
Severity: Medium
Advisory: GHSA-m52v-24p8-654f
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-22
Source: https://github.com/advisories/GHSA-m52v-24p8-654f
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <2.1.0
- crates.io: `surrealdb-core` — affected >=0 <2.1.0

## Details
Sorting table records using an `ORDER BY` clause with the `rand()` function as sorting mechanism could cause a panic due to relying on a comparison function that did not implement total order. This event resulted in a panic due to a recent [change in Rust 1.81](https://blog.rust-lang.org/2024/09/05/Rust-1.81.0.html#new-sort-implementations).

### Impact

A client that is authorized to run queries in a SurrealDB server would be able to query a table with `ORDER BY rand()` in order to potentially cause a panic in the sorting function. This would crash the server, leading to denial of service.

### Patches

The sorting algorithm has been updated to guarantee total order when shuffling records.

- Version 2.1.0 and later are not affected by this issue.

### Workarounds

Affected users who are unable to update may want to limit the ability of untrusted clients to run arbitrary SurrealQL queries in the affected versions of SurrealDB. To limit the impact of the denial of service, SurrealDB administrators may also want to ensure that the SurrealDB process is running so that it can be automatically re-started after a crash.

### References

- https://github.com/surrealdb/surrealdb/issues/4969
- https://github.com/surrealdb/surrealdb/pull/4989
- https://github.com/surrealdb/surrealdb/pull/4805
- https://github.com/surrealdb/surrealdb/pull/4906

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-m52v-24p8-654f
- https://github.com/surrealdb/surrealdb/issues/4969
- https://github.com/surrealdb/surrealdb/pull/4805
- https://github.com/surrealdb/surrealdb/pull/4906
- https://github.com/surrealdb/surrealdb/pull/4989
- https://github.com/surrealdb/surrealdb
