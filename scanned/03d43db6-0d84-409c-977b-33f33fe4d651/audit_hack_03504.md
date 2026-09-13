# [M] createAuction can overwrite existing auction

## Summary
Severity: Medium
Reporter: 0x4141
Source: https://github.com/sherlock-audit/2022-10-astaria/blob/main/lib/astaria-gpl/src/AuctionHouse.sol#L75
Type: audit-issue

## Details
# createAuction can overwrite existing auction

## Summary
With `AuctionHouse.createAuction`, an existing auction can be overwritten.

## Vulnerability Detail
In `AuctionHouse.createAuction`, it is not checked if an auction for the provided `tokenId` already exists.

## Impact
When an auction is overwritten, the bids are lost, leading to financial damage.

## Code Snippet
https://github.com/sherlock-audit/2022-10-astaria/blob/main/lib/astaria-gpl/src/AuctionHouse.sol#L75

## Tool used

Manual Review

## Recommendation
Do not allow overwriting existing auctions
