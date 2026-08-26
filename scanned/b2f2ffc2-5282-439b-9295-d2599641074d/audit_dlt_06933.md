# [M] Harvest can be frontrun

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-09-yaxis
Published: 2021-09-15
Source: https://github.com/code-423n4/2021-09-yaxis-findings/issues/140
Type: code-finding

## Details
# Handle

0xsanson


# Vulnerability details

## Impact
In the `NativeStrategyCurve3Crv._harvest` there are two instances that a bad actor could use to frontrun the harvest.

First, when we are swapping WETH to a stablecoin by calling `_swapTokens(weth, _stableCoin, _remainingWeth, 1)` the function isn't checking the slippage, leading to the risk to a frontun (by imbalancing the Uniswap pair) and losing part of the harvesting profits.

Second, during the `_addLiquidity` internal function: this calls `stableSwap3Pool.add_liquidity(amounts, 1)` not considering the slippage when minting the 3CRV tokens.


## Proof of Concept
https://github.com/code-423n4/2021-09-yaxis/blob/main/contracts/v3/strategies/NativeStrategyCurve3Crv.sol#L108

## Tools Used
editor

## Recommended Mitigation Steps
In the function `_harvest(_estimatedWETH, _estimatedYAXIS)` consider adding two additional estimated quantities: one for the swapped-out stablecoin and one for the minted 3CRV.
