# [H] H-01 | Incorrect Debt Update During Migration

## Summary
Severity: High
Contest weight: 0.2354
Dataset id: 2558
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the preferred Spartan Council pool contains multiple supported collateral type vaults the migration of a V2 staker's debt incorrectly deducts all of their associated debt from the collateral vault of the staker. However other collateral vaults may burden a portion of the reportedDebt delta which was experienced by the LegacyMarket when the staker migrated. For example (contrived example for simplicity): • User A migrates their account which has X debt • Upon a normal debt distribution X/2 of this debt would go to the USDe vault and X/2 to the SNX vault • The Spartan Pool has two vaults: USDe and SNX, split 50%/50% in terms of backing liquidity for the Legacy Market • The AssociateDebt module however deducts X debt from only the SNX vault with distributeDebtToAccounts • As a result the USDe vault delegators experience a loss due to the burden of X/2 debt which should have been corrected for.

## Recommendation
When associating debt for a pool with multiple backing vaults, reduce the amount of debt from all vaults corresponding to their contribution to the market. This way the associatedDebt is correctly drawn from all counterparties and correctly associated with the target account.
