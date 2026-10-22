# [H] H-02 | Faulty Quoting With Small Amounts

## Summary
Severity: High
Contest weight: 0.2170
Dataset id: 1966
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a new epoch is created, the Vault uses the assets in its reserves to deposit them as collateral in order to create a liquidity position. The vault will call quoteLiquidityPositionTokens to get the amount0 and amount1 that can be added as liquidity for the available collateral. However, Epoch.requiredCollateralForLiquidity() now adds 1 to loanAmount0 and loanAmount1. This means the actual required collateral for the position may exceed the available collateral in the vault. In result, the transaction will revert because of InsufficientCollateral() and the epoch creation will not be successful. This issue can occur with non-trivial amounts, for example 1e17.

## Proof of Concept
https://github.com/GuardianAudits/foil-fuzzing/commit/800a5b927bd0668f6eacb37158a3dc079de9d7f0

## Recommendation
Consider implementing higher minimum collateral amounts and documenting this behavior for clarity. Another option to consider is subtracting 1 wei from amount0 and amount1 when creating the LiquidityMintParams, which should account for the additional 1 wei.
