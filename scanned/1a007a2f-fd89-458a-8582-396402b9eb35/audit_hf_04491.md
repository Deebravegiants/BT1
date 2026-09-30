# [H] H-02 | Required Collateral Invalid For Partial Closes

## Summary
Severity: High
Contest weight: 0.2321
Dataset id: 22054
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the updateValidLp function the loanAmount0 and loanAmount are computed by deducting the respective tokensOwed from the loaned amount. However the amount credited to pay down the loan cannot exceed the loaned amount. Consider the following scenario: • Trader A opens a position which is initially all vEth liquidity • Price moves downwards, trader A’s position is now entirely vGas liquidity • Trader A decreases their position and receives all vGas from reducing their liquidity • Trader A’s tokensOwed0 are not reﬂected in a reduction of their loaned amount because they had no loaned amount0 initially. • Thus trader A does not receive any collateral back and instead must supply more collateral because the collateralization validation measures their position as being worth less. As a result partial decreases are prevented for positions in this scenario as the additionalCollateral is hardcoded to 0.

## Recommendation
Consider passing the tokensOwed0 and tokensOwed1 through to the collateralRequirementAtMinTick function and adding them to the availableAmount0 and availableAmount1 values respectively so that this value is not truncated to zero.
