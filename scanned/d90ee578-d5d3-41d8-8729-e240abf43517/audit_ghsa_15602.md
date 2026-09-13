# [H] Untrusted Query Object Evaluation in RPC API

## Summary
Severity: High
Advisory: GHSA-64f8-pjgr-9wmr
CWE: CWE-75
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-11
Source: https://github.com/advisories/GHSA-64f8-pjgr-9wmr
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <1.5.5
- crates.io: `surrealdb-core` — affected >=0 <1.5.2
- crates.io: `surrealdb` — affected >=2.0.0-beta.1 <2.0.0-beta.3

## Details
During the sign in and sign up operations through the SurrealDB RPC API, an arbitrary object would be accepted in order to support a wide array of types and structures that could contain user credentials. This arbitrary object could potentially contain any SurrealDB value, including an object representing a subquery. For this to materialize, this object would need to be encoded using the bincode serialization format instead of the default JSON serialization format or the additionally supported CBOR serialization format.

If a binary object containing a subquery were to be provided in this way, that subquery would be computed while executing the `SIGNIN` and `SIGNUP` queries defined by the database owner while defining a record access method. Since those queries are executed under a system user session with the editor role, an unauthenticated attacker may be able to leverage this behavior to select, create, update and delete non-IAM resources with permissions of a system user with the editor role.

### Impact

If a record access method was defined with a `SIGNIN` or a `SIGNUP` query and the SurrealDB RPC API was exposed to untrusted users, an attacker could be able to craft a binary object containing a subquery to provide in place of valid credentials when calling the `signin` and `signup` operations via the RPC API with the bincode serialization format. The attacker could use that subquery to select, create, update and delete resources in SurrealDB, but they would not be able to _directly_ view the results of the query. This method cannot be used to create, update or delete IAM resources, as access to those kind of resources requires the owner role.

### Patches

Objects provided as variables to the sign in and sign up methods are now recursively validated to ensure that they do not contain any non-computed values, which include subqueries and other data types that could potentially result in query execution.

- Version 1.5.5 and later are not affected by this issue.
- Version 2.0.0-beta.3 and later are not affected by this issue.

### Workarounds

Users unable to update may want to disallow access to the SurrealDB RPC API using the affected binary serialization formats by conservatively allowing only requests to the `/rpc` endpoint of the SurrealDB HTTP server with the `application/json` content type. If the RPC API is not used at all or only used by trusted clients, disallowing or restricting access to the `/rpc` endpoint of the SurrealDB HTTP server will also prevent exploitation. Alternatively, if filtering HTTP requests is not possible, record access methods that define `SIGNIN` and `SIGNUP` clauses may be temporarily removed to completely prevent potential attacks leveraging this issue.

### References

- [SurrealDB Documentation - Authentication (Record Users)](https://surrealdb.com/docs/surrealdb/security/authentication#record-users)
- [SurrealDB Documentation - RPC Protocol (Signup)](https://surrealdb.com/docs/surrealdb/integration/rpc#signup)
- [SurrealDB Documentation - RPC Protocol (Signin)](https://surrealdb.com/docs/surrealdb/integration/rpc#signin)

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-64f8-pjgr-9wmr
- https://github.com/surrealdb/surrealdb/commit/b7583a653a2c495a60630dffd663f506426db330
- https://github.com/surrealdb/surrealdb/commit/eab7ef5354168d4039f7f7b77042c99a52f770a6
- https://github.com/surrealdb/surrealdb
- https://surrealdb.com/docs/surrealdb/integration/rpc#signin
- https://surrealdb.com/docs/surrealdb/integration/rpc#signup
- https://surrealdb.com/docs/surrealdb/security/authentication#record-users
