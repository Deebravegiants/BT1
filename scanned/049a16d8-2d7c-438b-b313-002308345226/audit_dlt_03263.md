# [M] CurveStableMetapoolCollateral.tryPrice returns a huge but valid high price when the price oracle of pairedToken is timeout

## Summary
Severity: Medium
Chain: Smart contract
Component: 2023-07-reserve
Published: 2023-08-04
Source: https://github.com/code-423n4/2023-07-reserve-findings/issues/25
Type: code-finding

## Details
# Lines of code

https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/CurveStableMetapoolCollateral.sol#L83-L86
https://github.com/reserve-protocol/protocol/blob/9ee60f142f9f5c1fe8bc50eef915cf33124a534f/contracts/plugins/assets/curve/CurveStableCollateral.sol#L74-L98


# Vulnerability details

The CurveStableMetapoolCollateral is intended for 2-fiattoken stable metapools. The metapoolToken coin0 is pairedToken and the coin1 is lpToken, e.g. 3CRV. And the `config.chainlinkFeed` should be set for paired token. 

## Impact
The CurveStableMetapoolCollateral.price() high price will be about `FIX_MAX / metapoolToken.totalSupply()` when the price oracle of pairedToken is timeout. It is significantly more than the actual price. It will lead to unexpected pricing in the rewards trade and rebalance auctions. Further more, I think an attacker can trigger this bug proactively by out of gas, which can bypass the empty error message check because of the different call stack depth. But I have not verified the idea due to lack of time. So the issue here only details the high price caused by external factor, for example oracle timeout. Hope to add it under this issue if I have any other progress. Thanks.

## Proof of Concept
In the `CurveStableMetapoolCollateral.tryPrice` function, the pairedToken price is from `tryPairedPrice` function by the following codes:
```solidity
uint192 lowPaired;
uint192 highPaired = FIX_MAX;
try this.tryPairedPrice() returns (uint192 lowPaired_, uint192 highPaired_) {
    lowPaired = lowPaired_;
    highPaired = highPaired_;
} catch {}

function tryPairedPrice() public view virtual returns (uint192 lowPaired, uint192 highPaired) {
    uint192 p = chainlinkFeed.price(oracleTimeout); // {UoA/pairedTok}
    uint192 delta = p.mul(oracleError, CEIL);
    return (p - delta, p + delta);
}
```
So if the chainlinkFeed is offline(oracle timeout), the tryPairedPrice will throw an error which is catched by the empty catch block, and the price of pairedToken will be (0, FIX_MAX). 

And then the function `_metapoolBalancesValue` will use these pirces to get the total UoA of the metapool. The following codes are how it uses the price of pairedToken:
```solidity
aumLow += lowPaired.mul(pairedBal, FLOOR);

// Add-in high part carefully
uint192 toAdd = highPaired.safeMul(pairedBal, CEIL);
if (aumHigh + uint256(toAdd) >= FIX_MAX) {
    aumHigh = FIX_MAX;
} else {
    aumHigh += toAdd;
}
```
The `aumLow` has already included the UoA of LpToken, so it is non-zero. And the highPaired price now is FIX_MAX, which will mul the paired token balance by `Fixed.safeMul`. We can find the Fixed lib has handled overflow safely:
```solidity
function safeMul(
    uint192 a,
    uint192 b,
    RoundingMode rounding
) internal pure returns (uint192) {
    ...
    if (a == FIX_MAX || b == FIX_MAX) return FIX_MAX;
```
So the `aumHigh` from the `_metapoolBalancesValue` function will be FIX_MAX. The final prices are calculated by:
```
low = aumLow.div(supply, FLOOR);
high = aumHigh.div(supply, CEIL);
```
`supply` is the `metapoolToken.totalSupply()`. So if the supply is > 1 token, the `Fixed.div` won't revert. And the high price will be a huge but valid value < FIX_MAX.


## Tools Used
Manual review
## Recommended Mitigation Steps
Don't try catch the `this.tryPairedPrice()` in the `CurveStableMetapoolCollateral.tryPrice`, if it failed, just let the whole tryPrice function revert, the caller, for example refresh(), can catch the error.


## Assessed type

Context
