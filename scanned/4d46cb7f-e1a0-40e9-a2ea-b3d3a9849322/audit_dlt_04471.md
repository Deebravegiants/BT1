# [H] Wrong value assignment

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-opyn
Published: 2022-12-03
Source: https://github.com/sherlock-audit/2022-11-opyn-judging/issues/152
Type: sherlock-finding

## Details
pzeus

high

# Wrong value assignment

## Summary
Usage of a wrong variable 
## Vulnerability Detail
There is a wrong assignment of a variable which causes emitting wrong value for an event
## Impact
High
## Code Snippet
https://github.com/sherlock-audit/2022-11-opyn/blob/main/crab-netting/src/CrabNetting.sol#L744
## Tool used

Manual Review

## Recommendation
Change `auctionTwapPeriod` to `otcPriceTolerance`
