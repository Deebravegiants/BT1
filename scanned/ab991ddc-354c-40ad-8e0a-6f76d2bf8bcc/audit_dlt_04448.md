# [M] Missing check

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/209
Type: sherlock-finding

## Details
pzeus

medium

# Missing check

## Summary
Function parameter missing check
## Vulnerability Detail
There is no check if `_ethToDeposit` is less than `msg.value` plus the proceeds from the flash swap
## Impact
This could end up passing an incorrect value for `_ethToDeposit`
## Code Snippet
https://github.com/opynfinance/squeeth-monorepo/blob/main/packages/hardhat/contracts/strategy/CrabStrategyV2.sol#L315
## Tool used

Manual Review

## Recommendation
Check at the beginning of the function as mentioned [here](https://github.com/opynfinance/squeeth-monorepo/blob/main/packages/hardhat/contracts/strategy/CrabStrategyV2.sol#L310)
