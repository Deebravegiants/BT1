# [M] Shopper: Missing authorization on Product admin Livewire sub-form components

## Summary
Severity: Medium
Advisory: GHSA-h4mp-g9c6-xwph
CVE: CVE-2026-47742
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-h4mp-g9c6-xwph
Type: github-advisory

## Affected
- Packagist: `shopper/framework` — affected >=0 <2.8.0

## Details
## Impact

Sub-form Livewire components used in the product editor (`Edit`, `Inventory`, `Seo`, `Shipping`, `Files`) had no authorization on their `store()` method. Any authenticated panel user, regardless of role, could mutate any product's pricing, stock, SEO metadata, shipping dimensions, and attached media without holding `edit_products`.

The affected components accepted the product ID as a public Livewire property without `#[Locked]`, so an attacker could also target an arbitrary product by tampering with the wire payload from the client.

## Patches

Fixed in `v2.8.0`. Each sub-form `store()` now authorizes against `edit_products` and the product binding is locked.

Upgrade via:

```bash
composer require shopper/admin:^2.8
```

## Workarounds

None. Upgrade to `v2.8.0`.

## References

- Pull request: https://github.com/shopperlabs/shopper/pull/511
- CWE-862 Missing Authorization

## References
- https://github.com/shopperlabs/shopper/security/advisories/GHSA-h4mp-g9c6-xwph
- https://nvd.nist.gov/vuln/detail/CVE-2026-47742
- https://github.com/shopperlabs/shopper/pull/511
- https://github.com/shopperlabs/shopper
