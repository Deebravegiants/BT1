# [H] H-05 | removeAllFrom DoS With External Liquidity

## Summary
Severity: High
Contest weight: 0.5546
Dataset id: 21458
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the removeAllFrom function, the function is short circuited if there is 0 liquidityToRemove, however this value is based upon the amount that is deployed in Uniswap.
Therefore a malicious actor may add to this amount in order to stop this early return check from triggering when the getLiquidity mapping reports that there is no liquidity deployed there for the system.
In this scenario the function execution continues on to remove all of the attacker’s malicious liquidity from the range and then attempts to remove 0 liquidity from the range after it has been depleted.
This second attempt to remove liquidity will revert with the NP error from Uniswap.

## Recommendation
Add a second early return case right before the _removeLiquidity invocation:
```solidity
if (liquidityToRemove == 0) return (0, bAssetFees_, 0, reserveFees_);
```
