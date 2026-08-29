# [M] when `direction=1`   the direction on  pools could be wrong

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-11-dodo
Published: 2022-11-15
Source: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/56
Type: sherlock-finding

## Details
simon135

medium

# when `direction=1`   the direction on  pools could be wrong

## Summary
since we are changing `direction=1` when we change the value it will only `sellBase()`  not `sellQuote`.
So if `direction=1` then In the first iteration of the loop it's going to sell  quote tokens   but after that it's going to sell Base tokens  which I don't think it intended
## Vulnerability Detail
when a user calls `mixSwap` function and sets `directions =1` in the first iteration of the loop `directions` gets changed to zero and once it's set to zero `sellBase` function is always called.
## Impact
It can cause loss of funds in the most extreme cases but I don't think   intended and can make a user swap lost funds because they didn't sell quote tokens.
In the comments, it says this 
```solidity 
/// @param directions pool directions aggregation, one bit represents one pool direction, 0 means sellBase, 1 means sellQuote
```
which is not true  because 1  in the loop with bit shifting will be different.
## Code Snippet
```solidity 
        if (directions & 1 == 0) {
                IDODOAdapter(mixAdapters[i]).sellBase(
                    assetTo[i + 1],
                    mixPairs[i],
                    moreInfos[i]
                );
            } else {
                IDODOAdapter(mixAdapters[i]).sellQuote(
                    assetTo[i + 1],
                    mixPairs[i],
                    moreInfos[i]
            }
            directions = directions >> 1;
        }
```
https://github.com/sherlock-audit/2022-11-dodo/blob/main/contracts/SmartRoute/DODORouteProxy.sol#L292
## Tool used


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-dodo-judging/issues/56_
