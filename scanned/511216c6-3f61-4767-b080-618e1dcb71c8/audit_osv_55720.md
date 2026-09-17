# [M] SurrealDB: Writes in a PERMISSIONS clause bypass table permissions

## Summary
Severity: Medium
Advisory: GHSA-66r2-5gwj-gxm2
Aliases: CVE-2026-63733
Ecosystem: crates.io
Published: 2026-09-04
Source: https://osv.dev/vulnerability/GHSA-66r2-5gwj-gxm2
Type: osv

## Affected
- crates.io: `surrealdb-core` — affected >=0 <3.2.0

## Details
A `PERMISSIONS ... WHERE` clause is evaluated with permission enforcement disabled, so it can't recurse into its own checks. But the clause could also contain data-modifying statements, and these ran with enforcement still off — so evaluating a permission check could write to tables the caller cannot write.

For example:

```surql
DEFINE TABLE post PERMISSIONS FOR update
    WHERE (CREATE log SET at = time::now()) OR true;
```

Any user allowed to update a `post` now also creates a `log` record, even with no permission on `log`. The clause is evaluated once per matched record, so one statement can cause several writes.

### Impact

Only databases with a `PERMISSIONS` clause that contains a write are affected; `FULL`, `NONE`, and read-only clauses are not.

What an attacker **can** do:

- With permission to perform the guarded operation (a low-privileged or record user is enough), write to tables in their own database that their permissions would otherwise forbid, by triggering an operation the clause guards.
- Cause several writes from a single statement — the clause is evaluated once per matched record.
- Trigger unintended events, cascades, or data corruption on those tables.

What it **can't** do:

- Escape the caller's own namespace and database — a permission clause cannot switch namespace or database.
- Perform root- or namespace-level actions such as creating users; the caller's role still applies.
- Read hidden data — this is an integrity issue, not disclosure.

### Patches

Permission clauses must now be read-only: defining or importing one that contains a write is rejected, and any write attempted while a clause is evaluated is blocked at runtime, including writes reached through a called function. Read-only clauses are unaffected.

- Versions 3.2.0 and later are not affected by this issue.

### Workarounds

Users unable to patch should consider the following workarounds:

- Review your `PERMISSIONS` clauses and remove any containing `CREATE`, `UPDATE`, `DELETE`, `RELATE`, `INSERT`, or `UPSERT`.
- Limit who can define schema and vet imported data — such a clause must be defined before it can be triggered.

### Resources

- [DEFINE TABLE … PERMISSIONS](https://surrealdb.com/docs/surrealql/statements/define/table)
- [DEFINE FIELD](https://surrealdb.com/docs/surrealql/statements/define/field)
- `fix(core): reject writes in PERMISSIONS clauses and block writes during permission evaluation` (included in SurrealDB 3.2.0)

### Acknowledgements

Thank you to [sondt99](https://github.com/sondt99) for reporting this issue.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-66r2-5gwj-gxm2
- https://nvd.nist.gov/vuln/detail/CVE-2026-63733
- https://github.com/surrealdb/surrealdb/commit/1e4c3d743e1591f14f340cb627e56d98b6bd7fd7
- https://github.com/surrealdb/surrealdb/commit/afea699dfb3c8f274ab36861f8a95f5e98d82f1b
- https://github.com/surrealdb/surrealdb
- https://github.com/surrealdb/surrealdb/releases/tag/v3.2.0
- https://www.vulncheck.com/advisories/surrealdb-before-permissions-bypass-via-permissions-clause
