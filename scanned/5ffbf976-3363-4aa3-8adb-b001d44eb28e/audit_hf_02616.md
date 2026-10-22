# [M] M-4 StUSR Yield Stealing

## Summary
Severity: Medium
Contest weight: 0.3846
Dataset id: 14128
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
• RewardDistributor.sol#L50
```
Rewards in StUSR are vulnerable to yield stealing.
A hacker can sandwich the RewardDistributor.distribute() transactions from the public mempool:
1. In the first transaction, a hacker front-runs by staking a significant amount of USR in StUSR to become the primary stakeholder.
2. The transaction then occurs, distributing rewards in StUSR.
3. In the next transaction, the hacker back-runs by withdrawing their funds with a guaranteed profit.
This results in regular users losing the incentive to stake funds, as the hacker can capture all distributed rewards.

## Recommendation
We recommend using private mempools for reward distribution transactions.
