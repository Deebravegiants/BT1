# [C] The auction can be bricked

## Summary
Severity: Critical
Contest weight: 0.3941
Dataset id: 7548
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The English-style auction allows users to bid for a specific NFT and the user with the highest bid will win it.
However, every user can decide to withdraw their bid by calling withdrawBid and get their money back:
```solidity
function withdrawBid() public auctionActive nonReentrant {
    uint256 bidAmount = auction.bids[msg.sender];
    require(bidAmount > 0, "No bid to withdraw");
    auction.bids[msg.sender] = 0;
    (bool os, ) = payable(msg.sender).call{value: bidAmount}("");
    require(os, "Transfer to bidder failed");
    emit BidRefunded(msg.sender, bidAmount);
}
```
This means that the highest bidder can decide to withdraw their money at any time. This opens an attack vector that can easily brick the bidding functionality because the auction.highestBid is not reset.
For example, a user can take a flash loan (let's say 1000 ETH for simplicity), bid with the whole amount, and then withdraw. This will update the auction.highestBid to 1000 ETH but the funds will not be in the contract. Thus, the auction can't be ended as the endAuction will revert because of insufficient funds.
```solidity
function endAuction() public onlyOwner auctionActive {
    auction.active = false;
    (bool os, ) = payable(owner()).call{value: auction.highestBid}("");
    require(os, "Transfer to owner failed");
    emit AuctionEnded(auction.highestBidder, auction.highestBid);
}
```
This can happen unintentionally if the highest bidder needs to withdraw their ETH for some reason and no one else is willing to bid more.

## Recommendation
There is no easy fix to this issue. An example solution is to check if the withdrawBid is the highest bid and reset it but it will need to inform all of the other users.
