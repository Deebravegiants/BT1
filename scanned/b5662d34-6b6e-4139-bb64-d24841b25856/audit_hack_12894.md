# [M] The calculation of `uni_fees_total` is incorrect

## Summary
Severity: Medium
Reporter: GimelSec
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L265
Type: audit-issue

## Details
# The calculation of `uni_fees_total` is incorrect

## Summary

The calculation of `uni_fees_total` is incorrect in `Dca._calc_min_amount_out`, resulting in an incorrect value for `min_amount_out`.

## Vulnerability Detail

The calculation of `uni_fees_total` is simply the sum of `_fees`. However, this approach is incorrect and leads to an inaccurate `min_amount_out`.
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L265
```vyper
def _calc_min_amount_out(
    _amount_in: uint256, 
    _path: DynArray[address, 3], 
    _fees: DynArray[uint24, 2], 
    _twap_length: uint32, 
    _max_slippage: uint256
    ) -> uint256:

    uni_fees_total: uint256 = 0
    for fee in _fees:
        uni_fees_total += convert(fee, uint256)

    …
    min_amount_out = (min_amount_out * (FEE_BASE - uni_fees_total - _max_slippage)) / FEE_BASE
    …
```

The fees are applied when doing UniSwap’s swap. UniSwap subtract the fee from input token amount and calculate output amount from a smaller input amount. 
https://github.com/Uniswap/v3-core/blob/main/contracts/libraries/SwapMath.sol#L41
```solidity
    function computeSwapStep(
        uint160 sqrtRatioCurrentX96,
        uint160 sqrtRatioTargetX96,
        uint128 liquidity,
        int256 amountRemaining,
        uint24 feePips
    )
        internal
        pure
        returns (
            uint160 sqrtRatioNextX96,
            uint256 amountIn,
            uint256 amountOut,
            uint256 feeAmount
        )
    {
        …
            uint256 amountRemainingLessFee = FullMath.mulDiv(uint256(amountRemaining), 1e6 - feePips, 1e6);
            …
    }
}
```


Suppose the path contains two pools and the first fee is 10% and the second fee is also 10%.
* The output amount of first pool is (100 - 10)%
* The output amount of second pool is (90 - 9)%
* The final amount is 81%

So the actual `uni_fees_total` is 19%. But it would be 20% in `computeSwapStep`.




## Impact

Incorrect `uni_fees_total` leads to inaccurate `min_amount_out`.

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L265


## Tool used

Manual Review

## Recommendation

```diff
def _calc_min_amount_out(
    _amount_in: uint256, 
    _path: DynArray[address, 3], 
    _fees: DynArray[uint24, 2], 
    _twap_length: uint32, 
    _max_slippage: uint256
    ) -> uint256:

    uni_fees_total: uint256 = 0
    for fee in _fees:
-       uni_fees_total += convert(fee, uint256)
+       uni_fees_total = FEE_BASE- (FEE_BASE-uni_fees_total) * (FEE_BASE-fee) / FEE_BASE
    …
```
