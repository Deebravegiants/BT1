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
        return pairedAssetRegistry.toAsset(pairedToken).price();
    }
```

## Proof of Concept
`RToken.tryPrice` gets the BU (low, high) price from `basketHandler.price()` first. `BasketHandler._price(false)` core logic:
```solidity
for (uint256 i = 0; i < len; ++i) {
    uint192 qty = quantity(basket.erc20s[i]);

    (uint192 lowP, uint192 highP) = assetRegistry.toAsset(basket.erc20s[i]).price();

    low256 += qty.safeMul(lowP, RoundingMode.FLOOR);

    if (high256 < FIX_MAX) {
        if (highP == FIX_MAX) {
            high256 = FIX_MAX;
        } else {
            high256 += qty.safeMul(highP, RoundingMode.CEIL);
        }
    }
}
```
And the `IAsset.price()` should not revert. If the price oracle of the asset reverts, it just returns `(0,FIX_MAX)`. In this case, the branch will enter `high256 += qty.safeMul(highP, RoundingMode.CEIL);` first. And it won't revert for overflow because the Fixed.safeMul will return FIX_MAX directly if any param is FIX_MAX:
```solidity
function safeMul(
    ...
) internal pure returns (uint192) {
    if (a == FIX_MAX || b == FIX_MAX) return FIX_MAX;
```
So the high price is `FIX_MAX`, and the low price is reduced according to the share of qty.

Return to the `RToken.tryPrice`, the following codes uses `basketRange()` to calculate the low and high price for BU:
```solidity
BasketRange memory range = basketRange(); // {BU}

// {UoA/tok} = {BU} * {UoA/BU} / {tok}
low = range.bottom.mulDiv(lowBUPrice, supply, FLOOR);
high = range.top.mulDiv(highBUPrice, supply, CEIL);
```
And the only thing has to be proofed is `range.top.mulDiv(highBUPrice, supply, CEIL)` should not revert for overflow in unit192. Now highBUPrice = FIX_MAX, according to the `Fixed.mulDiv`, if `range.top <= supply` it won't overflow. And for passing the check in the `RToken._updateCachedPrice()`, the high price should be lower than FIX_MAX. So it needs to ensure `range.top < supply`.

The max value of range.top is basketsNeeded which is defined in `RecollateralizationLibP1.basketRange(ctx, reg)`:
```solidity
if (range.top > basketsNeeded) range.top = basketsNeeded;
```
And the basketsNeeded:RToken supply is 1:1 at the beginning. If the RToken has experienced a haircut or the RToken is undercollateralized at present, the basketsNeeded can be lower than RToken supply.

## Tools Used
Manual review
## Recommended Mitigation Steps
Add a BU price valid check in the `RToken.tryPrice`:
```solidity
function tryPrice() external view virtual returns (uint192 low, uint192 high) {
    (uint192 lowBUPrice, uint192 highBUPrice) = basketHandler.price(); // {UoA/BU}
    require(lowBUPrice != 0 && highBUPrice != FIX_MAX, "invalid price");
```


## Assessed type

Context
