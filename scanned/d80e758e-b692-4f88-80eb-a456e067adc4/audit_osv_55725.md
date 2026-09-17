# [H] SurrealDB: Custom API route lets authenticated callers override namespace/database scope via URL path

## Summary
Severity: High
Advisory: GHSA-848m-r628-vrxw
Aliases: CVE-2026-63735
Ecosystem: crates.io
Published: 2026-09-04
Source: https://osv.dev/vulnerability/GHSA-848m-r628-vrxw
Type: osv

## Affected
- crates.io: `surrealdb` — affected >=0 <3.2.0

## Details
An authenticated user scoped to one namespace/database could invoke a custom API (`DEFINE API`) belonging to a different namespace/database, reaching another tenant's endpoint.

The route `/api/{namespace}/{database}/{endpoint}` took the namespace and database from the URL and applied them to the caller's session before the endpoint was looked up or run, without checking that the caller's authenticated scope covered them. Because a custom API handler runs with permissions disabled (definer's rights), the endpoint's own `PERMISSIONS` clause was the only gate — open to everyone for a `PERMISSIONS FULL` endpoint. The `api::invoke()` function was affected the same way, resolving against the session's selected namespace/database (settable via the `surreal-ns` / `surreal-db` headers or `USE`).

### Impact

What an attacker **can** do:

- With valid credentials for any one namespace/database (a `VIEWER` is enough), invoke a custom API in another namespace/database by naming the victim scope in the URL.
- Read data that endpoint returns — including from `PERMISSIONS NONE` tables, since the handler runs with permissions disabled — or trigger any writes and side effects it performs.

What it **can't** do:

- Reach a scope without valid credentials for some namespace/database on the instance; this is not an unauthenticated bypass.
- Affect single-tenant deployments, or any deployment where callers already hold instance-wide (root) scope.

### Patches

The namespace/database is now validated against the caller's authenticated level — which the request cannot change — before the endpoint is resolved or run. A target scope outside that level is rejected with `403 Forbidden`, both at the HTTP entry point and at the dispatch step shared with `api::invoke()`. Root reaches any scope; namespace principals their namespace; database and record principals their exact namespace/database; anonymous callers remain governed by the endpoint's `PERMISSIONS`.

- Versions 3.2.0 and later are not affected by this issue.

### Workarounds

Users unable to patch should consider the following workarounds:

- Disable the custom API HTTP route via capabilities where it is not required.
- Treat separate deployments, not namespace/database boundaries, as the tenant isolation boundary on shared instances.
- Prefer a `PERMISSIONS WHERE` clause that checks the authenticated identity over `PERMISSIONS FULL` (reduces exposure but does not restore the boundary).

### Resources

- [SurrealQL Documentation — DEFINE API](https://surrealdb.com/docs/surrealql/statements/define/api)
- [SurrealDB Documentation — Capabilities](https://surrealdb.com/docs/surrealdb/security/capabilities)
- `fix(core/api): reject cross-tenant custom API access` (included in SurrealDB 3.2.0)

### Acknowledgements

SurrealDB thanks [sondt99](https://github.com/sondt99) for reporting this issue.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-848m-r628-vrxw
- https://nvd.nist.gov/vuln/detail/CVE-2026-63735
- https://github.com/surrealdb/surrealdb/commit/0938f88d196dc4eb11a82af343df3fffe9c195e2
- https://github.com/surrealdb/surrealdb/commit/75b7154f84904d047619b5a47b08d256254dceca
- https://github.com/surrealdb/surrealdb
- https://www.vulncheck.com/advisories/surrealdb-before-authentication-bypass-via-custom-api
