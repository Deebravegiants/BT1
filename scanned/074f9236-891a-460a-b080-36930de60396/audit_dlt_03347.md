# [M] `TributeAccrual` missing out-of-bounds checks

## Summary
Severity: Medium
Chain: Smart contract
Component: 2021-05-fairside
Published: 2021-05-26
Source: https://github.com/code-423n4/2021-05-fairside-findings/issues/46
Type: code-finding

## Details
# Handle

cmichel


# Vulnerability details

## Vulnerability Details
The `_addTribute` and `_addGovernanceTribute` functions underflow when there are no tributes:

```solidity
Tribute storage lastTribute = tributes[totalTributes - 1] = tributes[-1]; // underflow
```

## Impact
It's bad practice and the iteration with the offset in `totalAvailableTribute` will miss the initial tribute unless called with strange parameters that overflow themselves.

## Recommended Mitigation Steps
Add a special case `totalTributes (totalGovernanceTributes) == 0`.
