# [H] Laravel Backpack CRUD: CRUD panel query scopes are not enforced on Update, Delete, and Reorder (cross-tenant IDOR)

## Summary
Severity: High
Advisory: GHSA-vgmv-8xjc-6rch
CVE: CVE-2026-54180
CWE: CWE-639, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-vgmv-8xjc-6rch
Type: github-advisory

## Affected
- Packagist: `backpack/crud` — affected >=6.0.0 <6.8.14
- Packagist: `backpack/crud` — affected >=7.0.0 <7.0.38

## Details
## Summary

Backpack CRUD's list and read operations correctly apply any query scopes
registered via `addClause()` / `addBaseClause()` (e.g. tenant isolation, user
ownership). However, the **Update**, **Delete**, and **Reorder** operations
bypassed these scopes, fetching records directly from the unscoped model query.

An authenticated user who knows or can guess a record's primary key could
therefore update, delete, or reorder records that should be invisible to them —
a classic IDOR on write paths.

Applications that rely on `addBaseClause` for row-level access control
(multi-tenancy, per-user data isolation) are affected.

## Impact

Any Backpack CRUD panel that uses `addBaseClause` or `addClause` to restrict
which rows a user may access is affected on its write operations.
An authenticated low-privilege user can modify or delete records belonging to
other tenants / users.

## Patches

Apply the fixed release for your major version:

- **v6**: upgrade to **6.8.14** or later
- **v7**: upgrade to **7.0.38** or later

The fix ensures Update, Delete, and Reorder all resolve records through the same
scoped query used by the read side.

## Workarounds

If you cannot upgrade immediately, add explicit `Gate` / `Policy` checks in your
`CrudController`'s `update()`, `destroy()`, and `reorder()` methods to verify
the authenticated user is permitted to act on the resolved record.

## Credits

Reported by Vishal Shukla ([@shukla304](https://github.com/shukla304)).

## References
- https://github.com/Laravel-Backpack/CRUD/security/advisories/GHSA-vgmv-8xjc-6rch
- https://github.com/Laravel-Backpack/CRUD
- https://github.com/Laravel-Backpack/CRUD/releases/tag/6.8.14
- https://github.com/Laravel-Backpack/CRUD/releases/tag/7.0.38
