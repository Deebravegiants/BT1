# [M] 6.5 Unintended Order Types Possible

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected


Trading._matchOrders and _fillOrder miss sanity checks for combinations of makerAssetId,
takerAssetId and side in the passed order structs.

Eight combinations of side in [BUY, SELL], makerAssetId in
[ConditionalToken, Collateral], and takerAssetId in
[ConditionalToken, Collateral] are possible, but only two of them should be allowed. This
seems possible as the side seems redundant or colliding with the combinations (struct Order has
redundant fields).

This allows for matching of orders that are not intended. For example, matching of a BUY order with
maker asset YES and taker asset USDC to a SELL order with maker asset USDC and taker asset YES is
perfectly possible as long as the YES price in these orders is over 1 USDC (otherwise, the fee calculation
reverts).

Code correct

Unintended order types are no longer possible as fields makerAssetId and takerAssetId have been
replaced by a single field tokenId.
