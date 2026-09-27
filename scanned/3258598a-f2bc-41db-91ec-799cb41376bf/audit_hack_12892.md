# [M] Overflow danger in `sqrtPriceX96ToUint`

## Summary
Severity: Medium
Reporter: shealtielanz
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L41C1-L49C6
Type: audit-issue

## Details
# Overflow danger in `sqrtPriceX96ToUint`

## Summary
The `twap` in the `getSingleHopTwap()` function is gotten by calling the `sqrtPriceX96ToUint` function with `sqrtPriceX96`, `IERC20(poolToken0).decimals()` which can lead to an Overflow causing the `getSingleHopTwap()` to revert.
## Vulnerability Detail
`sqrtPriceX96ToUint()` will only work when the non-fractional component of `sqrtPriceX96` takes up to `32` bits. This represents a price ratio of `18446744073709551616`. With different token digits it is not unlikely that this ratio will be crossed which will make `getSingleHopTwap()`  revert
```solidity
    function sqrtPriceX96ToUint(uint160 sqrtPriceX96, uint8 decimalsToken0)
        public
        pure
        returns (uint256)
    {
        uint256 numerator1 = uint256(sqrtPriceX96) * uint256(sqrtPriceX96);
        uint256 numerator2 = 10**decimalsToken0;
        return FullMath.mulDiv(numerator1, numerator2, 1 << 192);
    }
```
## Impact
`getSingleHopTwap()` will most likely revert due to overflow.
## Code Snippet
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L41C1-L49C6
-  https://github.com/sherlock-audit/2023-06-unstoppable/blob/94a68e49971bc6942c75da76720f7170d46c0150/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L55
## Tool used

Manual Review

## Recommendation
check if `sqrtPrice > Q96`
**The code should be refactored like this:**
```solidity
    function sqrtPriceX96ToUint(uint160 sqrtPriceX96, uint8 decimalsToken0)
        public
        pure
        returns (uint256)
    {
       if (sqrtPriceX96 > Q96) {
           uint256 sqrtP = FullMath.mulDiv(sqrtPriceX96, 10 ** decimalsToken0 , Q96);
             return FullMath.mulDiv(sqrtP, sqrtP, 10 ** decimalsToken0);
           } else {
                   uint256 numerator1 = FullMath.mulDiv(sqrtPriceX96, sqrtPriceX96, 1);
                   uint256 numerator2 = 10 ** decimalsToken0;
           return FullMath.mulDiv(numerator1, numerator2, 1 << 192);
}
```
