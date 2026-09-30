# [H] LDTR-1 | Small Positions Backed By The Vault Token Cause Liquidations To Revert

## Summary
Severity: High
Contest weight: 0.1840
Dataset id: 19575
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the liquidateVaultToken function it is assumed that the totalAmount is always available for withdrawal from the vault since in many cases it would have been previously repaid to the vault in the MarketLiquidation.settleLiquidation function. However in the case where all funds are actively being borrowed from the vault and a small account is liquidated while the totalAmount is greater than the liabilities, there is not enough USDT to redeem from the vault and the liquidation will revert on line 397 in the DepositorVault.withdrawInternal function.

## Recommendation
Ensure the totalAmount is capped at the liabilities earlier on in the liquidation logic, this way there is always guaranteed to be enough USDT to redeem from the vault in the event that the user’s collateral is the vault token. Additionally, do not allow withdrawals from the DepositorVault to go below the available balance returned by getAvailableBalance. This way it is nontrivial to enter a scenario where there is no USDT left in the vault.
