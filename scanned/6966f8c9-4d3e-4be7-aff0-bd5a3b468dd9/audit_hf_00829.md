# [H] H-07 | Partial Vault Liquidations Ignore Rebalance

## Summary
Severity: High
Contest weight: 0.2269
Dataset id: 2565
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When liquidating a vault partially the markets are not rebalanced after the collateralLiquidated is seized by the liquidator. Therefore markets are not aware of this reduction in creditCapacity and cannot accurately determine if they are below the minimumCredit threshold, which may be likely if a vault has been partially liquidated. For example, BFP market and Perps Market rely on minimumCredit validations to decide whether increase orders should be allowed. Additionally, the vaultsDebtDistribution shares are not updated for the vault after the collateral value changes, which can lead to further mis-accounting of credit and debt spread across vaults.

## Proof of Concept
https://github.com/GuardianAudits/legacy-1/pull/6/commits/532e5b06bb0137c8b44c8751e51b90d567535387#diff-3d7ac216cfd17a1907d878223ef7603f69889d7911d6049a1a9e2b9444604722R201

## Recommendation
Be sure to call recalculateVaultCollateral function after the collateral is deducted from accounts in the partial vault liquidation case.
