# [H] Univ3Twap.sol : `sqrtPriceX96ToUint` incorrect price value computation

## Summary
Severity: High
Reporter: 0xpinky
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L41C14-L41C32
Type: audit-issue

## Details
# Univ3Twap.sol : `sqrtPriceX96ToUint` incorrect price value computation

## Summary

Function [sqrtPriceX96ToUint](https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L41C14-L41C32) divides the price by `2**192` But it should divide by `2**96`

## Vulnerability Detail

```vyper
    function sqrtPriceX96ToUint(uint160 sqrtPriceX96, uint8 decimalsToken0)
        public
        pure
        returns (uint256)
    {
        uint256 numerator1 = uint256(sqrtPriceX96) * uint256(sqrtPriceX96);
        uint256 numerator2 = 10**decimalsToken0;
        return FullMath.mulDiv(numerator1, numerator2, 1 << 192); ----------------> it should be 96 instead of 192
    }
```
As per [uniswap ](https://blog.uniswap.org/uniswap-v3-math-primer#fn-7)documentation, the value which is used to divide the number which is after X in sqrtPriceX96.

## Impact

Incorrect price value .

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L41C14-L49

## Tool used

Manual Review

## Recommendation

```vyper
    function sqrtPriceX96ToUint(uint160 sqrtPriceX96, uint8 decimalsToken0)
        public
        pure
        returns (uint256)
    {
        uint256 numerator1 = uint256(sqrtPriceX96) * uint256(sqrtPriceX96);
        uint256 numerator2 = 10**decimalsToken0;
        return FullMath.mulDiv(numerator1, numerator2, 1 << 192);  -(remove)
        return FullMath.mulDiv(numerator1, numerator2, 1 << 96);   +(add)
    }
```
