# [C] Shopper: Authorization bypass and RBAC privilege escalation in team settings

## Summary
Severity: Critical
Advisory: GHSA-c3qp-2ggw-xjg7
CVE: CVE-2026-47744
CWE: CWE-269, CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-c3qp-2ggw-xjg7
Type: github-advisory

## Affected
- Packagist: `shopper/framework` — affected >=0 <2.8.0

## Details
## Impact

Two distinct authorization defects in the team settings allowed any authenticated panel user to take over the RBAC system:

- `Settings/Team/Index` had no `mount()` authorization. Any authenticated user could load the page and use its public actions to create new roles and delete other users, including administrators.
- `Settings/Team/RolePermission` gated its write actions on the read-only `view_users` permission. Any user holding `view_users` could grant themselves or any other user arbitrary permissions, including `manage_users` and `edit_orders`, effectively escalating to full panel administrator from a read-only account.

Combined, these two defects allow a low-privilege authenticated user to obtain administrator privileges and remove the legitimate administrators from the panel.

## Patches

Fixed in `v2.8.0`:

- `Settings/Team/Index::mount()` now authorizes against `manage_users`.
- `Settings/Team/RolePermission` write actions now require `manage_users` instead of `view_users`.

Upgrade via:

```bash
composer require shopper/admin:^2.8
```

## Workarounds

None. Upgrade to `v2.8.0`.

## References
- https://github.com/shopperlabs/shopper/security/advisories/GHSA-c3qp-2ggw-xjg7
- https://nvd.nist.gov/vuln/detail/CVE-2026-47744
- https://github.com/shopperlabs/shopper/pull/511
- https://github.com/shopperlabs/shopper
