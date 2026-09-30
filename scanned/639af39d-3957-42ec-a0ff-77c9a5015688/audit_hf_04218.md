# [C] C-07 | LPs Can Claim Rewards While Avoiding Debt

## Summary
Severity: Critical
Contest weight: 0.3011
Dataset id: 21112
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LP’s which delegated their collateral can exit the pools between BFP flag and liquidate. On flag all of
the collateral is distributed instantly, while keeping totalDebt the same (non-sUSD collateral) since
the position still exists. However when liquidating totalDebt will change effectively assigning debt to
the LP providers.
This allows LPs who have already staked for some time (above requiredMinDelegationTime) to flag
a large position, claim the rewards in the payoutToken and then to decrease their exposure with
delegateCollateral to 0, skipping the debt exposure when the position gets liquidated.
Consider the following scenario:
1) Bob and Alice both delegated equal amounts of collateral.
2) 10 ETH is distributed upon liquidatable position being flagged.
3) Alice claims her 5 ETH and removes her delegation.
4) The position is liquidated.
5) The debt is solely distributed to Bob’s LP position, so the account’s debt is increased.
6) Alice can re-delegate her collateral and all of the distributed debt is still on Bob’s position.
Ultimately, Alice was able to avoid the socialization of debt while still gaining the same amount of
rewards from the RewardDistributor.

## Proof of Concept
https://github.com/GuardianAudits/synthetix-pocs-2/tree/POC_LP_FLAG_PROFIT

## Recommendation
This issue ultimately arises from awarding LPs with liquidated collateral before the liquidated
position has been cleared from the reportedDebt. Consider avoiding the distribution of all collateral
upon flagging. Instead, distribute collateral upon liquidatePosition, proportional with the amount of
size being liquidated or only once the position has been entirely liquidated.
