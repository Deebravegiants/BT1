# [M] Function `stabilize`

## Summary
Severity: Medium
Contest weight: 0.7051
Dataset id: 18161
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
MaltDataLab fetched `priceCumulative` directly from Uniswap V2 pool to calculate price of Malt token. However, it is noticed that Uniswap V2 pool use Solidity 0.5.16, which does not revert when overflow happen. In addition, it is actually commented in Uniswap code that

    // * never overflows, and + overflow is desired

```solidity
if (timeElapsed > 0 && _reserve0 != 0 && _reserve1 != 0) {
    // * never overflows, and + overflow is desired
    price0CumulativeLast += uint(UQ112x112.encode(_reserve1).uqdiv(_reserve0)) * timeElapsed;
    price1CumulativeLast += uint(UQ112x112.encode(_reserve0).uqdiv(_reserve1)) * timeElapsed;
}
```
However, MaltDataLab contracts use Solidity 0.8 and will revert when overflow. It will break the `stabilize()` function and always revert since `stabilize()` call to MaltDataLab contract to get state.

Please note that, with Solidity 0.5.16, when result of addition bigger than `max(uint256)`, it will overflow without any errors. For example, `max(uint256) + 2 = 1`.

So when `price0CumulativeLast` is overflow, the new value of `price0CumulativeLast` will be smaller than old value. As the result, when MaltDataLab doing a subtraction to calculate current price, it might get revert.

## Proof of Concept
Function `stabilize()` will call to `MaltDataLab.trackPool()` first:
```solidity
function stabilize() external nonReentrant onlyEOA onlyActive whenNotPaused {
    // Ensure data consistency
    maltDataLab.trackPool();
    ...
}
```
Function `trackPool()` used a formula that will revert when `priceCumulative` overflow in Uniswap pool. 
```solidity
price = FixedPoint
    .uq112x112(
      uint224(  
        // @audit might overflow with solidity 0.8.0
        (priceCumulative - maltPriceCumulativeLast) / 
          (blockTimestampLast - maltPriceTimestampLast)
      )
    )
```
Scenario:

  1. `maltPriceCumulativeLast = max(uint256 - 10)` and `price = 10, timeElapsed = 10`. So the new `priceCumulative = max(uint256 - 10) + 10 * 10 = 99 (overflow)`
  2. When doing calculation in Malt protocol, `priceCumulative < maltPriceCumulativeLast`, so `priceCumulative - maltPriceCumulativeLast` will revert and fail

## Recommendation
Consider using `unchecked` block to match handle overflow calculation in Uniswap V2.
