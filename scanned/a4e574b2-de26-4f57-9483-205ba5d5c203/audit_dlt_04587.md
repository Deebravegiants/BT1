# [H] Option amount can not be odd, truncation will happen

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-buffer
Published: 2022-11-22
Source: https://github.com/sherlock-audit/2022-11-buffer-judging/issues/75
Type: sherlock-finding

## Details
silviaxyz

high

# Option amount can not be odd, truncation will happen

## Summary
optionParams.amount never be odd number because of division with 2.

## Vulnerability Detail
Truncation happens when amount is odd number. Which makes `option.premium` truncated which makes settlementFee lower in line 137.

## Impact
High. There may not be any fee because trancation will happen for sattlementFee calculation.

## Code Snippet

https://github.com/sherlock-audit/2022-11-buffer/blob/main/contracts/contracts/core/BufferBinaryOptions.sol#L107-L149


## Tool used

Manual Review

## Recommendation
