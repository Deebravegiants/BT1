# [M] SurrealDB: Array element-level (field.*) SELECT permissions leak denied elements to record users

## Summary
Severity: Medium
Advisory: GHSA-8rw6-p7m8-63jp
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-14
Source: https://github.com/advisories/GHSA-8rw6-p7m8-63jp
Type: github-advisory

## Affected
- crates.io: `surrealdb` — affected >=0 <3.1.4

## Details
A `SELECT` permission defined on an array element (`DEFINE FIELD field.* … PERMISSIONS FOR select …`) is not enforced correctly for `RECORD` users. Instead of hiding the denied elements, the query leaks a subset of them: a deny-all returns the odd-indexed elements, and a per-element predicate keeps and drops the wrong ones.

The filter removed each denied element by index while walking the array forwards. Because removing an element shifts every later index down, each cut invalidated the indices still pending in the loop, leaving denied elements behind. Field-level permissions are enforced correctly; only the element (`field.*`) level is affected, and only for record users — root and record-owner sessions are not.

## Impact

What an attacker **can** do:

- As a record (scope) user, read array elements that an element-level (`field.*`) SELECT permission should hide, on any table they can already SELECT.
- Recover denied elements through both a deny-all and a `WHERE` predicate — the wrong elements are selected either way.

What it **can't** do:

- Bypass field-level SELECT permissions, which are evaluated correctly.
- Affect root or record-owner sessions, or cross namespace/database isolation.
- Modify data, escalate privileges, or affect availability (confidentiality only).

## Patches

The three permission-filtering paths (`doc/reduce.rs`, `doc/output.rs`, `exec/operators/scan/pipeline.rs`) now remove denied elements in reverse index order, so removing one element no longer shifts the elements still to be checked. Regression tests reproducing the issue were added.

The fix is included in SurrealDB 3.1.4.

## Workarounds

- Do not rely on element-level (`field.*`) permissions to hide data from record users; use field-level permissions, which are enforced correctly.
- Restrict record users from selecting tables whose schema uses element-level permissions.

## Resources

- [DEFINE FIELD](https://surrealdb.com/docs/surrealql/statements/define/field)
- [USERS](https://surrealdb.com/docs/learn/security/authentication/authentication)
- [DEFINE TABLE … PERMISSIONS](https://surrealdb.com/docs/surrealql/statements/define/table)
- `fix(sec): stop array element-level SELECT permissions leaking elements` (commit `8f89b260b`)

## References
- https://github.com/surrealdb/surrealdb/security/advisories/GHSA-8rw6-p7m8-63jp
- https://github.com/surrealdb/surrealdb/commit/8f89b260bb9692e5b0d58930793d482a8207eedc
- https://github.com/surrealdb/surrealdb
