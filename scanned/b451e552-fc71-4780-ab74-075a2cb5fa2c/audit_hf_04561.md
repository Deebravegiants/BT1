# [H] H-07 | Reward Sniping With AutoCompounder

## Summary
Severity: High
Contest weight: 0.1379
Dataset id: 22164
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When token rewards such as ARB are deposited into the TokenRewards contract, a large portion of it is expected to be transferred to AutoCompoundingPodLp which is a large holder of spTKNs. Then the next time a user interacts with AutoCompoundPodLp, _processRewardsToPodLp is called to compound the reward tokens into more LP, benefiting existing holders of aspTKN.

## Recommendation
As there is no penalty nor timelock for deposits and withdrawals, a user may front-run the deposit of reward tokens by depositing into AutoCompoundingPodLp so as to claim some of the rewards, and then back-run the deposit of rewards and withdraw from AutoCompoundingPodLp. Such extractive behavior results in less rewards for other users who are staked for the long term.
