# [M] SurrealDB: Field-level SELECT permissions bypassed via indexed COUNT fast paths

## Summary
Severity: Medium
Advisory: GHSA-c8jx-96c9-8xrp
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-c8jx-96c9-8xrp
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.0

## Details
A record user could learn the value of a hidden field by counting how many records match a guess.

When `DEFINE FIELD ... PERMISSIONS FOR select WHERE ...` hides a field's contents from a caller, and that field is indexed, running `SELECT count() FROM t WHERE hidden_field = "guess" GROUP ALL` returned a count greater than zero whenever a record actually had that value — even though the caller was never allowed to read the field directly. The query planner used an indexed-COUNT shortcut (`Index::Count`, `IndexCountScan`, or the legacy `Iterate Index Count` / `Iterate Index Keys` paths) that counts matching index entries and skips the permission check that would normally hide the value. The same query with `WITH NOINDEX` correctly returned `[]`, confirming the gap.

By repeating the count query with different guesses, an attacker can confirm or recover the contents of any restricted field they could not read through a normal `SELECT`.

### Impact

What an attacker **can** do:

- Confirm or recover values of a field protected by field-level SELECT permissions on any table they hold table-level SELECT on, provided the field is indexed.
- Repeat the query with different guesses to read restricted field contents one value at a time.

What it **can't** do:

- Read fields that are not indexed (the shortcut only fires when an index covers the predicate column).
- Cross table, database or namespace isolation boundaries.
- Modify data, escalate privileges, or affect availability.

### Patches

The legacy planner (`surrealdb/core/src/idx/planner/tree.rs`) and the streaming planner (`surrealdb/core/src/exec/planner/select/mod.rs`) now both refuse the indexed fast path when the WHERE / ORDER tree references a field governed by a non-`Full` SELECT permission:

- `resolve_indexes` skips any B-tree / unique index whose columns are governed by such a permission.
- A new `cond_touches_restricted_field` flag is propagated; `eval_count` refuses a dedicated `Index::Count` when set.
- The streaming planner adds `cond_touches_restricted_select_field`, a `RestrictedIdiomChecker` visitor that matches each idiom against the table's field-permission prefixes (loaded via the plan-time txn), and gates `IndexCountScan` emission on it.
- The fast paths are preserved for root / owner sessions via `should_check_perms_for_view`.

Versions 3.1.0 and later are not affected.

### Workarounds

Users unable to patch are advised to consider the following workarounds:

- Avoid `DEFINE INDEX` on fields whose values are protected by field-level SELECT permissions. The class of attack is specific to the indexed fast paths.
- Restrict the ability of record users to issue arbitrary `SELECT count() … GROUP ALL` queries against tables containing field-protected columns.
- Use namespace / database isolation as the primary boundary where feasible.

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-c8jx-96c9-8xrp
- https://github.com/surrealdb/surrealdb/pull/240
- https://github.com/surrealdb/surrealdb/commit/0c6dd021bb55b32a78a553c72bb9c0cdd414825f
- https://github.com/surrealdb/surrealdb
