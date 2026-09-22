# [M] `Univ3Twap.sqrtPriceX96ToUint` could suffer from overflow

## Summary
Severity: Medium
Reporter: GimelSec
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L46
Type: audit-issue

## Details
# `Univ3Twap.sqrtPriceX96ToUint` could suffer from overflow

## Summary

`Univ3Twap.sqrtPriceX96ToUint` should be aware of the overflow of `uint256(sqrtPriceX96) * uint256(sqrtPriceX96)`.


## Vulnerability Detail

The calculation in `sqrtPriceX96ToUint` is correct. But it doesn’t handle the potential overflow of  `uint256(sqrtPriceX96) * uint256(sqrtPriceX96)` if `uint256(sqrtPriceX96) > type(uint128).max` .
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L46
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

The library in Uniswap has the correct implementation that can prevent overflow.
https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol#L57
```solidity
    function getQuoteAtTick(
        int24 tick,
        uint128 baseAmount,
        address baseToken,
        address quoteToken
    ) internal pure returns (uint256 quoteAmount) {
        uint160 sqrtRatioX96 = TickMath.getSqrtRatioAtTick(tick);

        // Calculate quoteAmount with better precision if it doesn't overflow when multiplied by itself
        if (sqrtRatioX96 <= type(uint128).max) {
            uint256 ratioX192 = uint256(sqrtRatioX96) * sqrtRatioX96;
            quoteAmount = baseToken < quoteToken
                ? FullMath.mulDiv(ratioX192, baseAmount, 1 << 192)
                : FullMath.mulDiv(1 << 192, baseAmount, ratioX192);
        } else {
            uint256 ratioX128 = FullMath.mulDiv(sqrtRatioX96, sqrtRatioX96, 1 << 64);
            quoteAmount = baseToken < quoteToken
                ? FullMath.mulDiv(ratioX128, baseAmount, 1 << 128)
                : FullMath.mulDiv(1 << 128, baseAmount, ratioX128);
        }
    }
```

## Impact

`Univ3Twap.sqrtPriceX96ToUint` may overflow. 

## Code Snippet

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/utils/Univ3Twap.sol#L46

## Tool used

Manual Review

## Recommendation

Reference the implementation of UniSwap library
https://github.com/Uniswap/v3-periphery/blob/main/contracts/libraries/OracleLibrary.sol#L57
