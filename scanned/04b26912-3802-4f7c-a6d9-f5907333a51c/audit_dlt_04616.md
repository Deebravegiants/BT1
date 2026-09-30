# [M] increaser does not change

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-telcoin
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-telcoin-judging/issues/20
Type: sherlock-finding

## Details
bulej93

medium

# increaser does not change

## Summary
after setting the increaser for the first time it does not change
## Vulnerability Detail
the state variable increaser does change after been set for the first time by deployer
## Impact
this will make it impposible to replace the increase in the future which may lead to loss of rewards
## Code Snippet
https://github.com/sherlock-audit/2022-11-telcoin/blob/main/contracts/SimplePlugin.sol#L150-L154
   

## Tool used

Manual Review

## Recommendation
