# [H] H-01 | collateralRequirementAtMaxTick Underﬂow

## Summary
Severity: High
Contest weight: 0.2626
Dataset id: 22053
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In collateralRequirementAtMaxTick, this line can revert due to underﬂow: return totalLoanAmountInEth - maxAmount1; It is possible totalLoanAmountInEth to be less than maxAmount1, as the loan amount of each token is loanAmount - tokensOwed. This means that the position is already overcollateralized by the tokensOwed + liquidity position. Consider this scenario: 1. User opens liquidity position 2. They wash trade such that the fees paid for token0 and token1 exceed the loan amounts loanAmount0 and loanAmount1 The fees are stored in tokensOwed0 and tokensOwed1. Therefore the loanAmount - tokensOwed of both tokens are 0. This is logical because there’s actually no collateral required to back a position who's loans is entirely backed by collected fees. However, since maxAmount1 is greater than 0, then the equation return totalLoanAmountInEth - maxAmount1; will underﬂow. An example where loanAmountInEth becomes 0 was chosen to make the underﬂow obvious, but just a slight reduction in loanAmountInEth could make the underﬂow revert happen. This makes it impossible to increase or partially decrease liquidity for some liquidity positions.

## Recommendation
In the collateralRequirementAtMaxTick function, consider returning 0 if maxAmount1 > totalLoanAmountInEth.
