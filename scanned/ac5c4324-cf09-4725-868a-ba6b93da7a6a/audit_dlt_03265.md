# [M] User can't redeem from RToken based on CurveStableRTokenMetapoolCollateral when any underlying collateral of paired RToken's price oracle is offline(timeout)

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/21
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/CurveStableRTokenMetapoolCollateral.sol#L46-L54
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/CurveStableCollateral.sol#L119-L121
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/CurveStableMetapoolCollateral.sol#L122-L138


# Vulnerability details

The CurveStableMetapoolCollateral is intended for 2-fiattoken stable metapools that involve RTokens, such as eUSD-fraxBP. The metapoolToken coin0 is pairedToken, which is also a RToken, and the coin1 is lpToken, e.g. 3CRV. And the `CurveStableRTokenMetapoolCollateral.tryPairedPrice` uses `RTokenAsset.price()` as the oracle to get the pairedToken price:
```
function tryPairedPrice()
    ...
    returns (uint192 lowPaired, uint192 highPaired)
{
    return pairedAssetRegistry.toAsset(pairedToken).price();
}
```

## Impact
Users can't redeem from RToken when any underlying collateral of paired RToken's price oracle is offline(timeout). It can lead to a serious run/depeg on the RToken.

## Proof of Concept

First I submitted another issue named "RTokenAsset price oracle can return a huge but valid high price when any underlying collateral's price oracle timeout". It's the premise for this issue. Because this issue is located in different collateral codes, I split them into two issues.

The conclusion from the pre issue:
    
    If there is any underlying collateral's price oracle reverts, for example oracle timeout, the `RTokenAsset.price` will return a valid but untrue (low, high) price range, which can be described as `low = true_price * A1` and `high = FIX_MAX * A2`, A1 is `bh.quantity(oracle_revert_coll) / all quantity for a BU` and A2 is the `BasketRange.top / RToken totalSupply`.

Back to the `CurveStableRTokenMetapoolCollateral`. There are two cases that will revert in the super class `CurveStableCollateral.refresh()`.

The `CurveStableRTokenMetapoolCollateral.tryPairedPrice` function gets low/high price from `paired RTokenAsset.price()`. So when any underlying collateral's price oracle of paired RTokenAsset reverts, the max high price will be FIX_MAX and the low price is non-zero.

1. If the high price is FIX_MAX, the assert for low price will revert:
```
if (high < FIX_MAX) {
    savedLowPrice = low;
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/21_
