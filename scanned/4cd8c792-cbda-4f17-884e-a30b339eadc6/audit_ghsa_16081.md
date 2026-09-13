# [M] SurrealDB has an Uncaught Exception Handling Nonexistent Role

## Summary
Severity: Medium
Advisory: GHSA-jc55-246c-r88f
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-22
Source: https://github.com/advisories/GHSA-jc55-246c-r88f
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <2.1.0
- crates.io: `surrealdb-core` — affected >=0 <2.1.0

## Details
Roles for system users are stored as generic `Ident` values and converted as strings and into the `Role` enum whenever IAM operations are to be performed that require processing the user roles. This conversion expects those identifiers to only contain the values `owner`, `editor` and `viewer` and will return an error otherwise. However, the `unwrap()` method would be called on this result when implementing `std::convert::From<&Ident> for Role`, which would result in a panic where a nonexistent role was used.

### Impact

A privileged user with the `owner` role at any level in SurrealDB would be able to define a user with `DEFINE USER` with an nonexistent role, which would panic when being converted to a `Role` enum in order to perform certain IAM operations with that user. These operations included signing in with the user. This would crash the server, leading to denial of service.

### Patches

Unexistent roles are no longer accepted during parsing when defining a user. Even when successfully associated with a user, referencing unexistent roles will no longer result in a panic and will instead throw an `InvalidRole` error.

- Version 2.1.0 and later are not affected by this issue.

### Workarounds

Affected users who are unable to update may want to limit access to users with the `owner` role at any level to trusted parties only. To limit the impact of the denial of service, SurrealDB administrators may also want to ensure that the SurrealDB process is running so that it can be automatically re-started after a crash.

### References

- #5079
- #5092

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-jc55-246c-r88f
- https://github.com/surrealdb/surrealdb/pull/5079
- https://github.com/surrealdb/surrealdb/pull/5092
- https://github.com/surrealdb/surrealdb
