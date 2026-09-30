# [M] Multiple centralization vulnerabilities can break the protocol

## Summary
Severity: Medium
Contest weight: 0.1419
Dataset id: 16043
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Multiple methods in TopiaLpStaking are centralization vulnerabilities and some can be used to break the protocol for users: setRewardsToken can be used to update the rewardsToken address to a random one, making all reward claims revert, leading to stuck funds. setUniswapPair can be used to update the uniswapPair address to a random one, making all stakes/unstakes revert, leading to stuck funds. addLockupInterval can be used to add strange lockup intervals with huge multipliers. The setRewards method has multiple problems in itself: can be called multiple times, pushing the reward period away with every call. the _start value can be too further away in the future. the _end value can already have passed. the duration between _start and _end might be too large (for example 70 years). the contract balance of reward tokens is not validated - this can mean users won't be guaranteed to be able to claim their rewards.

## Recommendation
Make the rewardsToken, uniswapPair and lockupIntervals immutable variables, there shouldn't be a need to change them. Also make sure setRewards is callable just once. Discussion pashov: Resolved.
