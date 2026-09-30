# [M] M-37 | Vaults' Utilization Not Updated After Bad Debt

## Summary
Severity: Medium
Contest weight: 0.0955
Dataset id: 22209
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During liquidation in FraxlendPair, if bad debt was incurred, whitelistUpdate is called which updates of all whitelisted vaults (except the calling vault). Then the bad debt is realized via: totalAsset.amount -= _amountToAdjust before LendingAssetVault is updated again to reduce its own internal tracking for _totalAssets. Instead, the whitelistUpdate of all vaults should be performed after the bad debt is realized in FraxlendPair. As a result, all other vaults will assume a higher amount of available assets (did not account for lost assets from bad debt) and charge a higher interest.

## Recommendation
Call whitelistUpdate at the end of liquidate after all state changes have been made in FraxlendPair
