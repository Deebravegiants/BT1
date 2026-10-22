# [H] secondsPerLiquidityCumulativesDelta calculation can overflow

## Summary
Severity: High
Contest weight: 0.3102
Dataset id: 8013
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function consult() depends on the seconds per liquidity cumulative values from the Uniswap V3 Pool to calculate harmonicMeanLiquidity. This value represents the amount of second liquidity inside a tick range that is "active". It is noted that they utilize a function similar to the one implemented in Uniswap V3. However, this function implicitly relies on underflow/overflow when calculating secondsPerLiquidityCumulativesDelta. If underflow is prevented, certain operations that depend on fee growth may revert. Due to the use of a different Solidity version, these calculations could revert due to overflow. Although this implementation resembles the library provided by Uniswap, it is important to note that Uniswap uses Solidity 0.6, which does not revert on overflow, whereas this contract is using Solidity 0.8.
Reference: https://github.com/code-423n4/2023-05-maia-findings/issues/505
(int56[] memory tickCumulatives, uint160[] memory secondsPerLiquidityCumulativeX128s) = IUniswapV3Pool(pool).observe(secondsAgos);
int56 tickCumulativesDelta = tickCumulatives[1] - tickCumulatives[0];
uint160 secondsPerLiquidityCumulativesDelta = secondsPerLiquidityCumulativeX128s[1] - // @audit should use unchecked
secondsPerLiquidityCumulativeX128s[0];
The similar issue also exists when subtracting poolFeeGrowthInside in the function _fees().
amount0 = Math.mulDiv(
poolFeeGrowthInside0LastX128 - feeParams.positionFeeGrowthInside0LastX128,
feeParams.liquidity,

## Recommendation
Consider using unchecked when calculating secondsPerLiquidityCumulativesDelta or using Solidity version smaller than 0.8.
