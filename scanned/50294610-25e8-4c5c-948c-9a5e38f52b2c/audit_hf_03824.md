# [H] _calculateMaxBorrowCollateral calculates re-

## Summary
Severity: High
Contest weight: 0.5934
Dataset id: 20056
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calculating the amount to repay, _calculateMaxBorrowCollateral incorrectly applies unutilizedLeveragePercentage when calculating netRepayLimit. The result is that if the borrowValue ever exceeds liquidationThreshold * (1 - unutilizedLeveragePercentage) then all attempts to repay will revert.
AaveLeverageStrategyExtension.sol#L1110-L1118
```solidity
} else {
    uint256 netRepayLimit = _actionInfo.collateralValue
        .preciseMul(liquidationThresholdRaw.mul(10 ** 14))
        .preciseMul(PreciseUnitMath.preciseUnit().sub(execution.unutilizedLeveragePercentage));
    return _actionInfo.collateralBalance
        .preciseMul(netRepayLimit.sub(_actionInfo.borrowValue))
        .preciseDiv(netRepayLimit);
}
```
When calculating netRepayLimit, _calculateMaxBorrowCollateral uses the liquidationThreshold adjusted by unutilizedLeveragePercentage. It then subtracts the borrow value from this limit. This is problematic because if the current borrowValue of the set token exceeds liquidationThreshold * (1 - unutilizedLeveragePercentage) then this line will revert making it impossible to make any kind of repayment. Once no repayment is possible the set token can't rebalance and will be liquidated.
Once the leverage exceeds a certain point the set token can no longer rebalance

## Recommendation
Don't adjust the max value by unutilizedLeveragePercentage
