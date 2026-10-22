# [H] H-04 | Settlement Failure Due To Underflow

## Summary
Severity: High
Contest weight: 0.2266
Dataset id: 1982
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When settling a liquidity position, getCurrentPositionTokenAmounts is called to retrieve the corresponding vGas and vETH token amounts of the position, which are then later rebalanced during position.settle. The rebalancing process converts everything to ETH, adding all value to depositedCollateral and subtracting all debt from depositedCollateral. However, the calculation during getCurrentPositionTokenAmounts rounds down, which can cause the total value of the position (including the collateral) to be less than the total debt in some cases. This results in the settlement reverting due to an underflow in the following line: self.depositedCollateralAmount = self.borrowedVEth.

## Proof of Concept
https://github.com/GuardianAudits/foil-fuzzing/blob/9d5aa754651b3a688d8ba6b67577affb9dabde87/packages/protocol/test/fuzzing/FoundryPlayground.sol#L290

## Recommendation
Rounding should be accounted for when calculating the required collateral. Consider adjusting loanAmount0 and loanAmount1 up by 1 wei during calculation.
