# [M] having a faulty iPlugin attached to Staking Module can cause DOS to the Staking Module

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/15
Type: sherlock-finding

## Details
koxuan

medium

# having a faulty iPlugin attached to Staking Module can cause DOS to the Staking Module

## Summary
Many functions in Staking Module rely on external iPlugin calls. If one of the iPlugin calls fail, it will not only cause the other iPlugin to not go through, but also prevent function like `stake`  to fail and revert as it also make external calls to iPlugin 
## Vulnerability Detail

## Impact

## Code Snippet

## Tool used

Manual Review

## Recommendation
