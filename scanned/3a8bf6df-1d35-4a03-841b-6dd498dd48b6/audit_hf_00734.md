# [M] M-20 | Liquidation Prevented By Zero Vault Delegation

## Summary
Severity: Medium
Contest weight: 0.1261
Dataset id: 2285
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a PerpRewardDistributor is deployed it is assigned a list of poolCollateralTypes which it distributes rewards to. In the liquidateCollateral function, the BFP market distributes liquidated collateral to each poolCollateralType in the backing pool according to the value of collateral in each corresponding vault.
However if one of the vaults holds zero collateral then the distributeRewards call will attempt to distribute 0 rewards to 0 vault shares. This action reverts in the RewardDistribution.distribute function, where the totalSharesD18 value is validated to be nonzero.
As a result liquidation flagging or liquidation by margin only where the account holds the collateral token which would be distributed to the empty vault will be DoS'd.

## Recommendation
If the vault collateral or the reward amount is equal to 0, skip distributing to that vault.
