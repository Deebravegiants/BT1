# [M] proper constructor initializations checks

## Summary
Severity: Medium
Reporter: techOptimizor
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L78
Type: audit-issue

## Details
# proper constructor initializations checks

## Summary
proper constructor initializations checks
## Vulnerability Detail
Some of the contructor varibles was not checked if is been initialized correctly with sepcial regards to time. Time could be mistakenly set lower than the current block time or setting start and end time to same value which will be worst case scenario and it wont revert in moddule of stepsize. .
## Impact
Division by zero which will always revert because time is same or always returns end price because end time is lower than current block.timestamp

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L78

## Tool used

Manual Review

## Recommendation
```solidity
require(startTime >= block.timestamp && startTime < endTime)
```
