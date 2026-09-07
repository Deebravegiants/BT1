# [M] `totalTokenVotingPower` could be inaccurate

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-frankendao
Published: 2022-11-16
Source: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/76
Type: sherlock-finding

## Details
__141345__

medium

# `totalTokenVotingPower` could be inaccurate

## Summary

In `_propose()`, `proposalThreshold()` and `quorumVotes()` is computed and saved into the proposal. However, the base `totalTokenVotingPower` to calculate these 2 values could change after the creation of this proposal and before the vote, even during the same block but executed afterwards. This could result in inaccurate threshold and quorum later used in the proposal. And even voting manipulation by later increase the voting power.

This issue will be more significant when the `totalTokenVotingPower` is still low during the early stage.


## Vulnerability Detail

`totalTokenVotingPower` could change due to the following:
- There could be tokens minted between the quorum computation and the vote.
- As users `stake()/unstake()`, `totalTokenVotingPower` will change. 
- As user `castVote()` and delegate votes, `totalCommunityScoreData.votes` can also change.

As a consequence, after the `_propose()`, the base amount of `totalTokenVotingPower` could deviate from the real situation.

A malicious user could even inflate the voting power by have more token after the proposal creation, hence manipulating the result.



## Impact

- `proposalThreshold()` and `quorumVotes()` could be inaccurate if calculated on spot `totalTokenVotingPower`.
- malicious user could manipulate the proposal result by having multiple tokens after the proposal creation.


## Code Snippet

`totalVotingPower` can change anytime:
https://github.com/sherlock-audit/2022-11-frankendao/blob/main/src/Staking.sol#L546-L548

https://github.com/sherlock-audit/2022-11-frankendao/blob/main/src/Staking.sol#L520-L527

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-frankendao-judging/issues/76_
