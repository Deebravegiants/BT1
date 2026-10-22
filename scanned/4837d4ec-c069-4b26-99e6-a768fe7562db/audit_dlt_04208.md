# [M] Centralisation Risk

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/51
Type: sherlock-finding

## Details
Nyx

medium

# Centralisation Risk

## Summary
Admin can take all funds in the contract.
## Vulnerability Detail
DodoRouteProxy. superWithdraw() allows withdrawing any funds in the contract.
## Impact
Admin can rug pull the funds in the contract. Centralization should be avoided for users' trust.
## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L146-L154
## Tool used

Manual Review

## Recommendation
