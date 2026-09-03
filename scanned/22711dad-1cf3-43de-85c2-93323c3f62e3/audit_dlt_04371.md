# [M] `overdueBlocks` change could harm borrowers

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-union-finance
Published: 2022-11-04
Source: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/108
Type: sherlock-finding

## Details
__141345__

medium

# `overdueBlocks` change could harm borrowers

## Summary

The `overdueBlocks` can be changed instantly, borrowers could suddenly become overdue, the balance could be frozen. But this rule is harmful for the borrowers. Since a loan agreement by design should not be changed arbitrarily.


## Vulnerability Detail

Currently the `overdueBlocks` can be changed instantly, leaving no response time for the borrowers. 

In principal, when a loan is borrowed, the term should be fixed. If the term can be changed arbitrarily, at the first place it is against the purpose of the loan. And the borrowers interest will be harmed by sudden change.


## Impact

Borrowers have no time to respond to incident, balance could be frozen.



## Code Snippet

The `overdueBlocks` can be changed bigger or smaller:
https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/market/UToken.sol#L325-L327

The `checkIsOverdue()` check could return true after the change:
https://github.com/sherlock-audit/2022-10-union-finance/blob/main/union-v2-contracts/contracts/market/UToken.sol#L376-L382


## Tool used

Manual Review



_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-union-finance-judging/issues/108_
