# [M] RTokenAsset price oracle can return a huge but valid high price when any underlying collateral's price oracle timeout

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/20
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/RTokenAsset.sol#L163-L175
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/RTokenAsset.sol#L53-L69
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/p1/BasketHandler.sol#L329-L351


# Vulnerability details

The RTokenAsset is an implementation of interface `IRTokenOracle` to work as a oracle price feed for the little RToken.
RTokenAsset implements the `latestPrice` function to get the oracle price and saved time from the `cachedOracleData`, which is updated by `_updateCachedPrice` function:
```solidity
function _updateCachedPrice() internal {
    (uint192 low, uint192 high) = price();

    require(low != 0 && high != FIX_MAX, "invalid price");

    cachedOracleData = CachedOracleData(
        (low + high) / 2,
        block.timestamp,
        basketHandler.nonce(),
        backingManager.tradesOpen(),
        backingManager.tradesNonce()
    );
}
```
The `_updateCachedPrice` gets the low and high prices from `price()`, and updates the oracle price to `(low + high) / 2`. And it checks `low != 0 && high != FIX_MAX`.

The `RTokenAsset.price` just uses the return of `tryPrice` as the low price and high price, if `tryPrice` reverts, it will return `(0, FIX_MAX)`, which is a invalid pirce range for the oracle price check above. But if there is any underlying collateral's price oracle reverts, for example oracle timeout, the `RTokenAsset.price` will return a valid but untrue (low, high) price range, which can be described as `low = true_price * A1` and `high = FIX_MAX * A2`, A1 is `bh.quantity(oracle_revert_coll) / all quantity for a BU` and A2 is the `BasketRange.top / RToken totalSupply`.

## Impact
The RToken oracle price will be about `FIX_MAX / 2` when any underlying collateral's price oracle is timeout. It is significantly more than the actual price. It  will lead to a distortion in the price of collateral associated with the RToken, for example `CurveStableRTokenMetapoolCollateral`:
```solidity
    pairedAssetRegistry = IRToken(address(pairedToken)).main().assetRegistry();
    
    function tryPairedPrice()
    ...
    {
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-07-reserve-findings/issues/20_
