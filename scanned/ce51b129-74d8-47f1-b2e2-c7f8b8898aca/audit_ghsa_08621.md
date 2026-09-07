# [H] shopper/framework: Authorization bypass in multiple Livewire admin components

## Summary
Severity: High
Advisory: GHSA-f946-9qp6-vgch
CVE: CVE-2026-47740
CWE: CWE-285, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-f946-9qp6-vgch
Type: github-advisory

## Affected
- Packagist: `shopper/framework` — affected >=0 <2.8.0

## Details
## Impact

Multiple Livewire components in the admin panel allowed an authenticated low-privilege user to mutate data without the required permission:

- Order detail Filament actions (cancel, mark paid, mark complete, capture payment, archive, start processing) were callable with `read_orders` only and did not require `edit_orders`. `capturePayment` could trigger an actual PSP capture.
- Order shipments table actions (mark delivered, edit tracking) were callable with `browse_orders` only.
- Sub-form Livewire components for products (Edit, Inventory, Seo, Shipping, Files) had no authorization on `store()`, so any authenticated panel user could mutate product data without `edit_products`.
- `Settings/Team/Index` had no `mount()` authorization at all — any authenticated user could create roles and delete other users.
- `Settings/Team/RolePermission` gated its write actions on the read-only `view_users` permission, allowing privilege escalation via the RBAC system itself.
- `PaymentMethods`, `Currencies`, `Carriers` table toggles and per-record actions had no per-action permission check.
- `Customers/Create::store()` re-passed a Hidden `_password` form field into the create payload.

Several public Eloquent model properties on Livewire components were not `#[Locked]`, allowing client-side ID tampering.

A stored XSS surface existed on the product barcode field, which is rendered through `DNS1DFacade::getBarcodeHTML()` with `{!! !!}`.

## Patches

Fixed in `v2.8.0`. Upgrade via:

```bash
composer require shopper/admin:^2.8 shopper/cart:^2.8 shopper/core:^2.8
```

```shell
php artisan migrate
```

## Workarounds

None. Upgrade to `v2.8.0`.

## Resources

- Pull request: https://github.com/shopperlabs/shopper/pull/511
- CWE-862 Missing Authorization
- CWE-285 Improper Authorization

## References
- https://github.com/shopperlabs/shopper/security/advisories/GHSA-f946-9qp6-vgch
- https://nvd.nist.gov/vuln/detail/CVE-2026-47740
- https://github.com/shopperlabs/shopper/issues/510
- https://github.com/shopperlabs/shopper/pull/511
- https://github.com/shopperlabs/shopper/commit/fcd0c5920588702df5b874f432b1042abd77a50b
- https://github.com/shopperlabs/shopper
- https://github.com/shopperlabs/shopper/releases/tag/v2.8.0
