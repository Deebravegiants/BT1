# [M] Withdrawals should never be paused

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/21
Type: sherlock-finding

## Details
bulej93

medium

# Withdrawals should never be paused

## Summary
in smart contracts withdrawals should never be paused, deposits can be paused however in show of good faith withdrawals should be left open unless there is a time limit
## Vulnerability Detail
pausing withdrawals can create bad faith amongst the users. if they are unable to withdraw their funds they may feel rugged
## Impact
users feeling rugged 
## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L167-L172
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L178-L185
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L190-L196
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L202-L207
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/StakingModule.sol#L212-L219
## Tool used

Manual Review

## Recommendation
do not pause withdrawals
