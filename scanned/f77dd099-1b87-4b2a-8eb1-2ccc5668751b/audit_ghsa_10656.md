# [H] @saltcorn/data: Tenant user role is used for tenant creation role check

## Summary
Severity: High
Advisory: GHSA-9237-rg5p-rhfw
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-9237-rg5p-rhfw
Type: github-advisory

## Affected
- npm: `@saltcorn/data` — affected >=0 <1.4.4
- npm: `@saltcorn/data` — affected >=1.5.0-beta.0 <1.5.2
- npm: `@saltcorn/data` — affected >=1.6.0-alpha.0 <1.6.0-beta.2

## Details
## Summary

When a tenant admin is logged out of the root domain (e.g., saltcorn.com) but logged in to their own tenant space as admin, they can simply append `/tenant/create` to their tenant URL. The system reads the role from the tenant context (admin), and a new tenant is created on the **root domain** (in `PUBLIC SCHEMA > _sc_tenants`), rather than in the tenant's own `_sc_tenants` table.

If the same logic applies to other routes, a tenant admin effectively gains admin rights on the root domain.

## PoC

A tenant-created subtenant appears under the Saltcorn public schema instead of the tenant's own schema.

- Even when `role_id=1` is required for tenant creation on saltcorn.com (only admin can create tenants), existing tenant admins can still create new tenants because their local `role_id:1` is evaluated against the root domain.
- Even when `role_to_create_tenant` is set to `0` in the tenant's `_sc_config` schema, or removed entirely, the tenant admin can still create sub-tenants on the root domain — suggesting `role_to_create_tenant` is not being read at all.

## Impact

Tenant admins gain unauthorized admin-level access to the root domain. Any authenticated tenant admin can perform privileged operations (e.g., creating tenants) on the root domain by exploiting the role context mismatch.

## References
- https://github.com/saltcorn/saltcorn/security/advisories/GHSA-9237-rg5p-rhfw
- https://github.com/saltcorn/saltcorn
