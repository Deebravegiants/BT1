# [M] GLOBAL-2 | Lack Of Liquidation Incentives

## Summary
Severity: Medium
Contest weight: 0.0873
Dataset id: 20529
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
According to the Dolomite whitepaper, “Liquidations forcefully repay any debt that is owed by a
borrower by transferring an equivalent amount of collateral from the borrower to the liquidator, plus a
liquidation penalty of 5%.”
The penalty is used as a reward for performing the liquidation and maintaining protocol solvency.
However, the integration lacks a reward for liquidations in the modules, leaving no incentive for a
user to trigger the prepareForLiquidation function if the unwrapping and swap into the Core protocol
succeeds.

## Recommendation
Consider providing the liquidator a reward in the output token for the liquidation.
