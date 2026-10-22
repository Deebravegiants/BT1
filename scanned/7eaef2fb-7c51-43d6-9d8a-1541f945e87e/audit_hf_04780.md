# [M] Incorrect calculation for total pool holding

## Summary
Severity: Medium
Contest weight: 0.4093
Dataset id: 22629
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The amount of pool's total holding is calculated with wrong formula, thus result in wrong liquidity index.
In _updateIndexes function of ReserveLogic.sol:
```solidity
uint256 totalPoolHoldings = IERC20(underlyingAsset).balanceOf(aTokenAddress) +
    // pool liquidity
    IERC20(reserve.stableDebtTokenAddress).totalSupply() + // total stable debt
    IERC20(reserve.variableDebtTokenAddress).totalSupply(); // total variable debt
```
As shown in the code snippet, totalPoolHoldings is calculated by summing up current balance of underlying asset and total debts. The calculated amount does not reflect correct amount because:
1. balance of underlying asset does not reflect correct value because it might be affected by flashloan.
2. debt amount does not reflect latest value because it does not count debt to accrue.
As a result, totalPoolHoldings does not represent correct number and it causes wrong liquidity index.
Liquidity index is calculated incorrectly which affects balance of depositors.

## Recommendation
Instead of summing up balance and debt, aToken.totalSupply() function has to used. It is the same way as how the AAVE V2 handles fees accrued from flashloan.
