# [M] <= should be used instead of < in getPriceAt() function

## Summary
Severity: Medium
Reporter: 0xeix
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L108
Type: audit-issue

## Details
# <= should be used instead of < in getPriceAt() function

## Summary

In MerittDutchAuction.sol, in the getPriceAt() function  <= should be used instead of < when comparing current time to the startTime 

## Vulnerability Detail

Current implementation of getPriceAt() checks whether time < startTime and if so, it returns startPrice. But the problem is that startPrice is also should be used at startTime

## Impact

startPrice will be miscalculated instead of just returning startPrice

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L108

## Tool used

Manual Review

## Recommendation

Change < on <=:

 if(time <= startTime)
