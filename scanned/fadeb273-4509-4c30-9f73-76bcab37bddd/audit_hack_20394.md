# [M] 5.2.5 Incorrect result rounding inUniswapV2Library.getAmountIn().

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** UniswapV2Library.sol#L128, UniswapV2Library.sol#L

**Description:** UniswapV2Library.getAmountOut()andUniswapV2Library.getAmountIn()are used to compute
output and input amounts for swapping, respectively. By design (i.e. in Uniswap 2), these functions are counter-
parties to each other: an input amount should have only one respective output amount (given that pool reserves
and the swap fee don't change), and vice versa. However, theUniswapV2Librarycontract computes swap fee
amount differently in the functions:

1. InUniswapV2Library.getAmountOut(), the fee is applied to the input amount before the output amount
    is calculated (UniswapV2Library.sol#L100). Notice that the fee amount (amountIn * 3 / 1000) is sub-
    tracted from the input amount–this results in an amount that's rounded up (the division rounds down, and
    thus the difference will be rounded up). In Uniswap V2, however, the result is always rounded down
    (UniswapV2Library.sol#L49).
2. UniswapV2Library.getAmountIn()is identical to Uniswap V2 (UniswapV2Library.sol#L56-L58). Thus, the
    result is rounded down.

The difference in rounding in the two functions will impact "exact output" swaps: in some scenarios, the actual
output amount will be greater than the one requested by the user by 1 wei; the input amount will be greater by 1
wei as well. Due to the maximum input amount check (V2SwapRouter.sol#L98), some "exact output" swaps can
fail.

**Recommendation:** Consider the following change:


```
--- a/contracts/modules/uniswap/v2/UniswapV2Library.sol
+++ b/contracts/modules/uniswap/v2/UniswapV2Library.sol
@@ -125,7 +125,8 @@ library UniswapV2Library {
{
if (reserveIn == 0 || reserveOut == 0) revert InvalidReserves();
if (!route.stable) {
```
- amountIn = (amountOut * 1000 * reserveIn) / ((reserveOut - amountOut) * 997) + 1;
+ amountIn = (amountOut * reserveIn) / (reserveOut - amountOut);
+ amountIn = (amountIn * 1000) / 997 + 1;
    } else {
       revert StableExactOutputUnsupported();
    }

**Velodrome:** The recommended fix to make the fee application consistent across both the universal router and the
pools has been applied in commit 44ca157f.

**Spearbit:** Fixed as recommended in commit 44ca157f.
