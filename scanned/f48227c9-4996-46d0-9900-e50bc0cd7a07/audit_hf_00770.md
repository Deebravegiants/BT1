# [C] C-05 | Wrongful Liquidity Burn

## Summary
Severity: Critical
Contest weight: 0.2307
Dataset id: 2396
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a position is executed, all of the liquidity at that position is burned. A user can also cancel their order after a position has been executed, which also burns the user's share of liquidity. Therefore, the following scenario can occur which will result in permanent loss of funds:
• User1 creates limit order at (60,120)
• Swap pushes to tick 180, limit order is executed. Liquidity is burned.
• Swap pushes the price back down to tick 0.
• User2 creates limit order at (60,120)
• User1 can cancel their original limit order that's already been executed.
• User2's liquidity has been burned and they cannot cancel their order. Orders at this position will revert when executed, also causing system-wide DOS for swaps around these ticks.

## Proof of Concept
https://gist.github.com/fatherGoose1/555e9531cf880ce06d9a9abd9016a0ac

## Recommendation
The early return userPositions[poolId][positionKey][user].claimablePrincipal != ZERO_DELTA needs to be amended to also include if the position is not active. This if clause can never be reached because claimablePrinciple is never non-zero at this point. The only check should be for position.isActive to indicate whether the position has been executed or not.
