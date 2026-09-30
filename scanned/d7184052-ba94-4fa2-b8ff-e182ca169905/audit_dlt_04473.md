# [M] Sanity check

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/112
Type: sherlock-finding

## Details
pzeus

medium

# Sanity check

## Summary
Potential uint underflow
## Vulnerability Detail
On this [line](https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L281) an error might occur when trying to `usdBalance[msg.sender] - _amount`
## Impact

## Code Snippet
https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L281
## Tool used

Manual Review

## Recommendation
I would suggest making a sanity check before that:
`if (usdBalance[msg.sender] >= _amount)`
