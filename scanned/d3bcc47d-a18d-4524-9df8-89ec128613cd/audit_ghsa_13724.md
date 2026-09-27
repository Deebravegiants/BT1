# [M] @vendure/core's insecure currencyCode handling allows wrong payment amounts

## Summary
Severity: Medium
Advisory: GHSA-wm63-7627-ch33
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-11-17
Source: https://github.com/advisories/GHSA-wm63-7627-ch33
Type: github-advisory

## Affected
- npm: `@vendure/core` — affected >=0 <2.1.3

## Details
### Impact

Currently, in many Vendure deployments it's possible to select any currencyCode (really any, doesn't need to be assigned to the channel) and pay through Mollie and Stripe in that particular currencyCode.
The prices are not transformed. The result is the Order is in Payment Settled in the foreign currency.
See SS, CZK is not in the channel.
I've tested with Mollie and Stripe it both works.

**Further notes**

After looking into this further and with help from the comments below, the root cause of this vulnerability is the ability to specify an arbitrary `currencyCode` as a query parameter to an API call, and then Vendure will use this and pass it to the rest of the system as `RequestContext.currencyCode`.

The solution is to add validation to the passed `currencyCode` to ensure that it matches one of the available `availableCurrencyCodes` of the active Channel.

Furthermore, an additional check has been added for when the currencyCode changes during the AddingItems stage - in this case we need to re-calculate the prices in the new currency.

### Patches
v2.1.3

### Workarounds
You can define a custom OrderProcess [onTransitionStart function](https://docs.vendure.io/guides/core-concepts/orders/#intercepting-a-state-transition) which can verify the order's `currencyCode` is as expected before allowing the transition to the `ArrangingPayment` state.

## References
- https://github.com/vendure-ecommerce/vendure/security/advisories/GHSA-wm63-7627-ch33
- https://github.com/vendure-ecommerce/vendure/commit/5e506fd8ba9f7e20030c329e62af1140d906121f
- https://github.com/vendure-ecommerce/vendure
