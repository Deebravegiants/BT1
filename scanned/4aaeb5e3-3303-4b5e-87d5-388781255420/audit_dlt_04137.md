# [H] A borrower can claim a NFT back with a tiny bid at auction

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-astaria
Published: 2022-11-07
Source: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/213
Type: sherlock-finding

## Details
hansfriese

high

# A borrower can claim a NFT back with a tiny bid at auction

## Summary

The house accepts all bids regardless of the amount and it releases the NFT to the winner when `endAuction` is called.
A borrower can waits until the auction starts and create a bid with a tiny amount and then call `endAuction` to claim the NFT back.

## Vulnerability Detail

The function `createBid` does not check the amount and process the incoming payment and remembers it as a last bidder.
In the function `endAuction` at AuctionHouse.sol#L166, the house removes the lien tokens for the collateral NFT and releases it to the 'winner' without checking if the winner bid amount is greater than the `reservePrice`.

```solidity
// AuctionHouse.sol#L93
function createBid(uint256 tokenId, uint256 amount) external override {
    address lastBidder = auctions[tokenId].bidder;
    uint256 currentBid = auctions[tokenId].currentBid;
    uint256 duration = auctions[tokenId].duration;
    uint64 firstBidTime = auctions[tokenId].firstBidTime;
    require(
      firstBidTime == 0 || block.timestamp < firstBidTime + duration,
      "Auction expired"
    );
    require(//@audit bids are accepted as long as the amount is over than the previous bid by some percentage, so tiny amount is accepted at first
      amount > currentBid + ((currentBid * minBidIncrementPercentage) / 100),
      "Must send more than last bid by minBidIncrementPercentage amount"
    );

    // If this is the first valid bid, we should set the starting time now.
    // If it's not, then we should refund the last bidder
    uint256 vaultPayment = (amount - currentBid);

    if (firstBidTime == 0) {
      auctions[tokenId].firstBidTime = block.timestamp.safeCastTo64();
```

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-astaria-judging/issues/213_
