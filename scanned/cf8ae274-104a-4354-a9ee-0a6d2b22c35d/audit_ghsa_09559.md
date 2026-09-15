# [M] shopper/framework: Race condition on Discount.usage_limit allows silent over-redemption

## Summary
Severity: Medium
Advisory: GHSA-9rh9-hf3w-9fgg
CVE: CVE-2026-47741
CWE: CWE-362
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-9rh9-hf3w-9fgg
Type: github-advisory

## Affected
- Packagist: `shopper/cart` — affected >=0 <2.8.0

## Details
## Impact

`CreateOrderFromCartAction::execute` previously created the `Order` row before checking and incrementing the discount's `total_use` counter. Under concurrent checkout pressure (Black Friday, flash sale, viral coupon), the global `usage_limit` was silently exceeded: orders were committed with the discount fully applied to `price_amount` while the counter blocked at `usage_limit`. The merchant had no signal that an over-redemption had occurred.

A second related bug: `usage_limit_per_user` was effectively a no-op because the counter it relied on (`DiscountDetail.total_use`) was never incremented anywhere in the codebase. The per-user check therefore always saw `0` uses and validation passed regardless of how many times the same customer had previously redeemed the coupon. For `eligibility = Everyone` the per-user limit could not fire at all because the underlying `DiscountDetail` row only exists for `eligibility = Customers`.

Direct financial loss: each over-redemption is a discount the merchant did not intend to grant.

## Patches

Fixed in `v2.8.0`. `CreateOrderFromCartAction` now:

- Reserves the discount slot atomically before the order row is created, inside the same `DB::transaction` with `lockForUpdate` and a compare-and-swap on `total_use`.
- Throws `DiscountLimitReachedException::global` and rolls back the transaction when the global limit was exhausted between cart validation and commit. No order is committed.
- Throws `DiscountLimitReachedException::perUser` and rolls back when the discount is restricted to one use per customer and the customer has already redeemed it.
- Snapshots `discount_id`, `discount_code`, `discount_type`, `discount_value_at_apply` and `discount_currency_code` onto the `orders` table for resilience against later discount edits or deletions.

`DiscountValidator` was updated to perform the same Order-based per-user check at cart-apply time so the rejection is surfaced before checkout.

Upgrade via:

`composer require shopper/cart:^2.8 shopper/core:^2.8`
`php artisan migrate`

## Workarounds

None. Upgrade to `v2.8.0`.

## Resources

- Issue: https://github.com/shopperlabs/shopper/issues/510
- Pull request: https://github.com/shopperlabs/shopper/pull/511
- CWE-362 Concurrent Execution using Shared Resource with Improper Synchronization

## References
- https://github.com/shopperlabs/shopper/security/advisories/GHSA-9rh9-hf3w-9fgg
- https://nvd.nist.gov/vuln/detail/CVE-2026-47741
- https://github.com/shopperlabs/shopper/issues/510
- https://github.com/shopperlabs/shopper/pull/511
- https://github.com/shopperlabs/shopper/commit/fcd0c5920588702df5b874f432b1042abd77a50b
- https://github.com/shopperlabs/shopper
- https://github.com/shopperlabs/shopper/releases/tag/v2.8.0
