# [M] A user can make a higher bet without increasing the bet price

## Summary
Severity: Medium
Contest weight: 0.0837
Dataset id: 10485
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol lets users auction off their NFTs. The owner can set min bet amount. Users can put bets and
at the end of the auction the highest bidder gets the NFT. The problem is that a user may bet the same
amount as the current highest bet and be the highest bidder. This is possible because of the way the
highestBid is compared:
require(msg.value >= auctionNfts[_auctionId].heighestBid, less
than highest bid price");

## Recommendation
Change GhostNFTMarketplace::bidPlace to so it only updates the highest bidder if the new bid is
higher, not equal.
- require(msg.value >= auctionNfts[_auctionId].heighestBid, less
than highest bid price");
+ require(msg.value > auctionNfts[_auctionId].heighestBid, less
than highest bid price");
