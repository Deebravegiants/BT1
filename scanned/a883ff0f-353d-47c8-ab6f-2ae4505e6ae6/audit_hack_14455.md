# [M] The price does not uniformly decrease in a Dutch auction

## Summary
Severity: Medium
Reporter: ashirleyshe
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L118C17-L118C28
Type: audit-issue

## Details
# The price does not uniformly decrease in a Dutch auction

## Summary
The price does not uniformly decrease in a Dutch auction.

## Vulnerability Detail
Assume the block interval is expected to have a timestamp of exactly 12 seconds.
The timestamp of the next block is `block.timestamp + 12 sec` and each step has a different price. 
```solidity
uint256 timePassed = time - startTime;
uint256 totalSteps = (endTime - startTime) / stepSize;
uint256 currentStep = timePassed / stepSize;
```
For example, when we have `stepSize=25`, blocks 0 to 2 are step 0, and blocks 3 to 4 are step 1. This shows that the price does not uniformly decrease in the auction as time passes.

| block            | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 |20 |21| 22|23|24|25|26|27|
|-------------|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|----|----|----|----|----|----|----|
| currentStep | **0** | **0** | **0** | 1 | 1 | 2 | 2 | 3 | 3 | 4 | 4  | 5  | 5  | 6  | 6  | 7  | 7  | 8  | 8  | 9| 9| 10 | 10 | 11 | 11 | 12 | 12 |12|
| timePassed  | 0|12|24|36|48|...

## Impact

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L118C17-L118C28

## Tool used

Manual Review

## Recommendation
Align the startTime and stepSize.
