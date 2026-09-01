# [H] Order of operations affects prices / amounts

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/216
Type: sherlock-finding

## Details
Deivitto

high

# Order of operations affects prices / amounts

## Summary
Order of operations affects prices / amounts. This is a problem due to precision and division truncate, mostly if it also affects money/tokens

## Vulnerability Detail
Solidity integer division might truncate. Rather than dividing before multiplying, performing multiplication before division can avoid loss of precision.

## Impact
Smaller prices and amounts than real ones will be used

## Code Snippet

- Affects `usdcAmount`
https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L703
- Affects `usdcAmount`
https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L713
- Affects `portion.crab`
https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L588
- Affects `portion.eth`
https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L592
- Affects `portion.eth`
https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L605
- Affects `crabFairPrice`
https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L788-L789
## Tool used

Manual Review

## Recommendation

Reorder the operations for avoiding losses

For example:

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/216_
