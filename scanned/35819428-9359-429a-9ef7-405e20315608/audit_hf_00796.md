# [H] H-17 | Users Can Avoid Liquidations

## Summary
Severity: High
Contest weight: 0.1974
Dataset id: 2532
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can borrow funds from pools using the PositionManager contract, as long as the position remains healthy, verified by riskEngine.isPositionHealthy(position).
The isPositionHealthy function has a flaw, as it has a condition where it can revert:
if (totalDebtValue != 0 && totalDebtValue < MIN_DEBT) revert RiskModule_DebtTooLow(position, totalDebtValue);
The liquidate function uses isPositionHealthy to avoid liquidating healthy positions, but if the position is not healthy and the totalDebtValue is less than MIN_DEBT, the liquidation fails.
Although isPositionHealthy is checked when a position borrows assets, the eth value of the debt can decrease below MIN_DEBT.

## Recommendation
Consider removing the MIN_DEBT check from RiskModule and add it only to the borrow and repay functions in PositionManager.
