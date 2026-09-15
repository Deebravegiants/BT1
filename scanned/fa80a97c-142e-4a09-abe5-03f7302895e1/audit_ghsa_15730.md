# [M] SurrealDB vulnerable to Improper Authentication when Changing Databases as Scope User

## Summary
Severity: Medium
Advisory: GHSA-gh9f-6xm2-c4j2
CWE: CWE-287
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-07-11
Source: https://github.com/advisories/GHSA-gh9f-6xm2-c4j2
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <1.5.4
- crates.io: `surrealdb` — affected >=2.0.0-alpha.1 <2.0.0-alpha.6
- crates.io: `surrealdb-core` — affected >=0 <1.5.1

## Details
Authentication would not be properly validated when an already authenticated scope user would use the `use` method or `USE` clause to switch working databases in a session. If there was a user record in the new database with identical record identifier as the original record that the user authenticated with in the original database, this could result in the user being able to perform actions under the identity of the unrelated user in the new database. This issue does not affect system users at any level.

By default, record identifiers are randomly generated with sufficient complexity to prevent the identifier collision required to trigger this issue. However, the issue may trigger in situations where multiple databases in the same SurrealDB instance are using explicitly defined or incremental record identifiers to identify users on an identically named table.

### Impact

Under the circumstances described above, a user who has an authenticated session as a scope user in a database could become authorized to query data under the identity of a specific scope user associated with an identical record identifier in a different database within the same SurrealDB instace if the `PERMISSIONS` clause would allow it due to relying exclusively on the `$auth` parameter, which would point to the impersonated user. The impact is limited to the single user with matching record identifier.

The impact of this issue is mitigated if the table `PERMISSIONS` clause explicitly checks for an scope that only exists in the specific database (e.g. `$scope = "production"`) or certain claims of the authentication token (e.g. `$token.email = "example@example.com"`), both of which would remain unchanged in the session of the authenticated user after changing databases. Permissions will default to `NONE` if there is no `PERMISSIONS` clause, which also mitigates this impact of this issue.

### Patches

- Version 1.5.4 and later are not affected by this issue.
- Version 2.0.0-alpha.6 and later will not be affected by this issue.

### Workarounds

Users unable to update may want to ensure that table `PERMISSIONS` clauses explicitly check that the `$scope` parameter matches a scope that is uniquely named across databases in the same SurrealDB instance. Ensuring that record identifiers for users are automatically generated or explicitly generated to be unique across databases may also be sufficient to mitigate this issue, as the `$auth` parameter will not link to any user record and any `PERMISSIONS` clauses restricting authorization based on the authenticated user should fail to successfully evaluate.

### References

- https://github.com/surrealdb/surrealdb/pull/4335

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-gh9f-6xm2-c4j2
- https://github.com/surrealdb/surrealdb/pull/4335
- https://github.com/surrealdb/surrealdb/commit/492f8378d57968dbdf5e63fad41b6ff59bba0b80
- https://github.com/surrealdb/surrealdb
