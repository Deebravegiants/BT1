# [H] SurrealDB has an Uncaught Exception Handling Parsing Errors on Empty Strings

## Summary
Severity: High
Advisory: GHSA-qjrv-v6qp-x99x
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-08
Source: https://github.com/advisories/GHSA-qjrv-v6qp-x99x
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=2.0.0 <2.0.4
- crates.io: `surrealdb-core` — affected >=2.0.0 <2.0.4

## Details
The error rendering code from the parser would panic when handling failed parsing of queries where the error occurred when converting an empty string to a SurrealDB value. This would be the case when casting an empty string to a `record`, `duration` or `datetime`, as well as potentially when parsing an empty string to JSON or providing an empty string to the `type::field` and `type::fields` functions.

### Impact

A client that is authorized to run queries in a SurrealDB server would be able to execute a malformed query which would fail to parse when converting an empty string and cause a panic in the error rendering code. This would crash the server, leading to denial of service.

### Patches

- Version 2.0.4 and later are not affected by this issue.

### Workarounds

Affected users who are unable to update may want to limit the ability of untrusted clients to run arbitrary SurrealQL queries in the affected versions of SurrealDB. To limit the impact of the denial of service, SurrealDB administrators may also want to ensure that the SurrealDB process is running so that it can be automatically re-started after a crash.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-qjrv-v6qp-x99x
- https://github.com/surrealdb/surrealdb/pull/4923
- https://github.com/surrealdb/surrealdb/commit/709d6efe901dbf3e207b4fc2ebc30775595efc16
- https://github.com/surrealdb/surrealdb
