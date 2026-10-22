# [M] StartTime not validated which could lead to incorrect Price

## Summary
Severity: Medium
Reporter: jokr
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
Type: audit-issue

## Details
# StartTime not validated which could lead to incorrect Price

## Summary

StartTime not validated which could lead to incorrect Price

## Vulnerability Detail

The `startTime` property is not validated in the constructor, which means that it can be set to a value that is less than the `current time`. This could lead to an auction being started before it is supposed to start, and the `getPrice` function would return a lower price than expected.

For example, if the `startTime` property is set to 0, the `getPrice` function would return a price that is less than the `startPrice` property immediately after deployment. This is not desirable.

## Impact

1. Price of the NFT would be lower than expected.
2. To ensure that the auction is correct, the owner must redeploy both the NFT and auction contracts. This is a waste of deployment costs.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L68-L87
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L99-L124

## Tool used

Manual Review

## Recommendation

Validate startTime is greater that or equal to current time in the constructor by adding
`require(startTime_ >= block.timestamp);`
