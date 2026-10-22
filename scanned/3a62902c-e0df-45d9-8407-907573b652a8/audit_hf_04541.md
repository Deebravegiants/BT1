# [M] M-21 | Vaults With Zero Delegation Prevent Liquidations

## Summary
Severity: Medium
Contest weight: 0.1138
Dataset id: 22105
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The LiquidationAssetmanager contract contains an array of addresses known as
poolDelegatedCollateralTypes.
When an account undergoes liquidation, the distribution of its collateral takes place within the
distributeCollateral function of this contract.
This particular function iterates over all pool collateral types, or vaults, and executes
distributeRewards for each of them in proportion to the amount held by the vault.
By tracing the sequence of calls, we eventually arrive at the distribute function within
RewardDistributon.sol. In this function, an attempt to distribute a reward to 0 vault delegators will
result in an error and cause a revert.

## Recommendation
To address this issue, we recommend implementing a check to skip the distribution process if either
the vault's collateral amount or the reward amount is equal to 0. This way, the liquidation process will
not be hindered by attempting to distribute rewards to vaults with zero collateral.
