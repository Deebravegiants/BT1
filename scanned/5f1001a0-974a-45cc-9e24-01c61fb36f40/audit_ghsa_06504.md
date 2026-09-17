# [M] SurrealDB: USE NS/DB implicit creation bypasses DEFINE authorization

## Summary
Severity: Medium
Advisory: GHSA-wp87-mgvq-5j93
CWE: CWE-862, CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-wp87-mgvq-5j93
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
An anonymous caller could create new namespaces and databases on a running SurrealDB instance without holding `DEFINE NAMESPACE` or `DEFINE DATABASE` permission.

`USE NS <name>` and `USE DB <name>` automatically create the target when it does not exist. The three places `USE` is handled — the RPC `use` method, `Datastore::process_use`, and the SurrealQL executor — did not check whether the caller was allowed to create the resource. Under default capabilities any session reached this path, including an unauthenticated guest.

### Impact

What an attacker **can** do:

- Create new namespaces and databases without `DEFINE NAMESPACE` / `DEFINE DATABASE` permission. An unauthenticated guest is enough under default capabilities.
- Recreate a parent namespace that an operator deliberately dropped, using a stale namespace-Editor token, by running `USE NS <dropped> DB anything`.
- Exhaust catalog storage by repeatedly creating new resources.

What it **can't** do:

- Read or modify data inside any pre-existing namespace or database.
- Escalate to root or namespace-owner privileges on existing resources.
- Affect deployments running with `auth_enabled=false`.

### Patches

All three `USE` entry points now check whether the caller has `DEFINE NAMESPACE` / `DEFINE DATABASE` authority before creating a missing target. Sessions still update their context regardless of authorization, so SDKs that send `use` before `signin` continue to work — only the catalog creation step is gated. The parent-namespace side-effect path is closed by the same check.

Versions 3.1.0 and later are not affected.

### Workarounds

- Set `--deny-arbitrary-query *` for guest principals to remove the entry point.
- Run with `--auth` and require all callers to `signin` before issuing `use`.
- Revoke namespace-level tokens promptly when a namespace is dropped.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-wp87-mgvq-5j93
- https://github.com/surrealdb/surrealdb/commit/f3ee3bd55533c14f1fa3e69ce18fc8904c1ce3f9
- https://github.com/surrealdb/surrealdb
