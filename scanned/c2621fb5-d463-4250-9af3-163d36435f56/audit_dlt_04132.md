# [M] cancelAuction() can  cancel "the completed Auction"

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-10-astaria
Published: 2022-11-07
Source: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/239
Type: sherlock-finding

## Details
bin2chen

medium

# cancelAuction() can  cancel "the completed Auction"

## Summary
AuctionHouse#cancelAuction() can  cancel "the completed Auction"

## Vulnerability Detail
When the auction has ended (time is up), and the bid amount is less than reservePrice, then it still can #cancel(), this does not make sense, after the end of the auction should only #endAuction()

## Impact
after the end of the auction should cancel

## Code Snippet
https://github.com/sherlock-audit/2022-10-astaria/blob/main/lib/astaria-gpl/src/AuctionHouse.sol#L210

```solidity
  function cancelAuction(uint256 auctionId, address canceledBy)
    external
    requiresAuth
  {
    require(
      auctions[auctionId].currentBid < auctions[auctionId].reservePrice,
      "cancelAuction: Auction is at or above reserve"
    );
  /**** only check price , no check if end ****/
```

## Tool used

Manual Review

## Recommendation
require not end
```solidity
  function cancelAuction(uint256 auctionId, address canceledBy)
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/239_
