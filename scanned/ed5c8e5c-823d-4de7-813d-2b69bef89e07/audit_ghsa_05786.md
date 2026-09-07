# [M] Laravel Backpack CRUD: HasMany/MorphMany relation fields allow cross-tenant record re-parenting (IDOR) via attachManyRelation

## Summary
Severity: Medium
Advisory: GHSA-42vx-43vc-x6pr
CVE: CVE-2026-57570
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-42vx-43vc-x6pr
Type: github-advisory

## Affected
- Packagist: `backpack/crud` — affected >=7.0.0 <7.0.47
- Packagist: `backpack/crud` — affected >=6.0.0 <6.8.15

## Details
## Vulnerability Details

Affected area: HasMany / MorphMany relation handling during CRUD create and update operations  
CWE: CWE-862 — Missing Authorization  
Severity: Medium  
CVSS: 6.5 — CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N

### Summary

Backpack CRUD contained an authorization issue in the way certain HasMany and MorphMany relationship fields were processed during create and update operations.

When an admin form allowed users to manage multiple related records, Backpack could update related model records based on submitted primary keys without sufficiently checking whether those records were eligible to be associated with the current parent model.

This could allow an authenticated, low-privileged admin user to affect related records outside the intended authorization or tenancy boundary, if the affected CRUD form exposed this type of relationship field.

### Root Cause

The vulnerable logic processed submitted relationship values and updated matching related records without consistently limiting those updates to records that already belonged to the current parent model, or to records allowed by the developer-defined relation scope.

As a result, a user with permission to edit one parent record could potentially cause unrelated child records to be reassigned, detached, nulled, or deleted as a side effect of saving the form.

This issue is separate from earlier fixes that scoped direct CRUD operations on the main entity. Those protections covered the model being directly edited, but they did not fully cover secondary models modified through relationship-saving logic.

### Impact

An authenticated admin user with access to an affected CRUD operation could potentially cause unauthorized changes to related records.

Possible impact includes:

- Unauthorized reassignment of related records across users, parents, or tenants.
- Unauthorized detachment or removal of related records.
- Data integrity issues in multi-tenant or permission-sensitive applications.

The issue requires an authenticated admin account with edit access to a CRUD entity that exposes an affected HasMany or MorphMany multiple-relation field.

### Affected Conditions

An application may be affected when all of the following are true:

- A Backpack CRUD form exposes a multiple-selection field for a HasMany or MorphMany relation.
- The related model contains records that should not be attachable or removable by the current admin user.
- The application relies on tenant, ownership, or authorization boundaries for those related records.
- The application has not added its own additional validation or authorization checks around submitted relation values.

### Recommended Fix

Backpack should scope relationship attach and detach operations so they only affect records that are valid for the current parent model and relation context.

The fix should ensure that related records are filtered through the relation’s intended query scope, ownership rules, or other developer-defined constraints before any update, detach, null, or delete operation occurs.

Applications using affected relationship fields should also validate submitted relation IDs server-side, especially in multi-tenant or permission-sensitive admin panels.

### Verification

The issue was confirmed through an internal PHPUnit test against Backpack’s existing Testbench fixtures.

The test demonstrated that, before the fix, a related record owned by one parent model could be reassigned to another parent model through the relationship-saving flow, without an explicit ownership or authorization check.

After applying the fix, submitted relationship values are constrained before related records are modified, preventing unauthorized reassignment or removal.

## References
- https://github.com/Laravel-Backpack/CRUD/security/advisories/GHSA-42vx-43vc-x6pr
- https://github.com/Laravel-Backpack/CRUD
- https://github.com/Laravel-Backpack/CRUD/releases/tag/6.8.15
- https://github.com/Laravel-Backpack/CRUD/releases/tag/7.0.47
