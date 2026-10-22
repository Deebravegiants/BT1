# [M] dodoMutliSwap is not check whether splitNumber is sorted ASC and starts with 0 or not

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/88
Type: sherlock-finding

## Details
Chom

medium

# dodoMutliSwap is not check whether splitNumber is sorted ASC and starts with 0 or not

## Summary
dodoMutliSwap is not check whether splitNumber is sorted ASC and starts with 0 or not

If splitNumber is not stored ASC then splitNumber[i - 1] >= splitNumber[i] is possible, in this case this loop will be skipped

```solidity
for (uint256 j = splitNumber[i - 1]; j < splitNumber[i]; j++) { 
```

And will proceed to another group of split which may cause an unexpected behavior

## Vulnerability Detail
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L387-L442

## Impact
If splitNumber is not sorted ASC or does not start with 0, it won't revert but it will cause the logic to broken.

## Code Snippet
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L387-L442

## Tool used
Manual Review

## Recommendation
Check if splitNumber is sorted ASC and starts with 0 before proceed.
