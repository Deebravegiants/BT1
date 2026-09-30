# [M] M-01 | Reward Distributor Is Not Future-Proof

## Summary
Severity: Medium
Contest weight: 0.1483
Dataset id: 2258
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
We have one reward distributor per collateral as speciﬁed with this: globalMarginConﬁg.supported[runtime.collateralAddress].rewardDistributor and a PerpRewardDistributor instances can be linked to only one pool as we can see from their _poolId variable. During liquidation, nonUsd collaterals are distributed only to that pool distributor is connected with. Although currently pool creation is done by governance only, this will create problems when the pool creation became permissionless. After creating pools became permissionless, when a pool owner choose to back a BFP-Market instance that they don't own, they won't be able to get something from liquidations (at least nonUsd collaterals). This will either disincentivize pool creators to back a BFP-Market instance that they don't own (which is against SNX's vision), or a pool owner that is not aware of this situation will back these markets and LP's will lose funds.

## Recommendation
Change how rewards are distributed and allow multiple pool Id's. While distributing skim all pool's collaterals and distribute accordingly. It is important to be extra cautious while implementing this because it can create new attack vectors. Pool addition should be done timely to capture reward distributions correctly.
