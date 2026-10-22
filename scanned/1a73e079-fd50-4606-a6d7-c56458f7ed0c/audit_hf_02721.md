# [M] Users can frontrun rebase to extract profits at the expense of long-term stakers

## Summary
Severity: Medium
Contest weight: 0.1459
Dataset id: 14798
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The StakingToken contract is susceptible to a frontrunning attack during the rebase process. Users who monitor on-chain events can detect when a rebase is imminent, especially if they can predict or observe an increase in the total supply in the calldata. They can exploit this by: Front-running the Rebase: Depositing a significant amount of tokens just before the rebase occurs, thereby increasing their share of the total supply. Benefiting from the Rebase: When the rebase increases the total supply, these users receive a disproportionate share of the newly minted tokens relative to their short-term stake. Back-running with Withdrawal: Immediately requesting an unstake after the rebase, capturing the rebase rewards without a long-term commitment. This behavior allows opportunistic users to extract undue profits, effectively diluting the value of long-term stakers' holdings. It undermines the fairness and intended reward distribution of the staking mechanism.

## Recommendation
Enforce a minimum staking duration before users are allowed to unstake or withdraw their tokens. This prevents immediate withdrawal after benefiting from a rebase.
