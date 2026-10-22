# [M] Owners can rug the users and not send anything

## Summary
Severity: Medium
Contest weight: 0.3852
Dataset id: 7552
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The auction is designed to reward the winning bid with a specific NFT. However, when the auction ended, nothing was sent to the winner, only the funds were transferred to the owner:
```solidity
function endAuction() public onlyOwner auctionActive {
    auction.active = false;
    (bool os, ) = payable(owner()).call{value: auction.highestBid}("");
    require(os, "Transfer to owner failed");
    emit AuctionEnded(auction.highestBidder, auction.highestBid);
}
```
This opens up a rug factor as the owners will withdraw auction.highestBid but can decide to not send the NFT to the winner of the auction.

## Recommendation
Transfer the NFT inside the endAuction call so the users are sure that there is a guaranteed prize.
