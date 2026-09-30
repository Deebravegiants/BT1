# [H] The bid function will revert because of a wrong check

## Summary
Severity: High
Contest weight: 0.7600
Dataset id: 7549
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The bid function can be called when users want to bid again and increase their bid. This happens by adding the current msg.value to all the previous bids and calculating it in newBidTotal variable:
```solidity
function bid() public payable auctionActive {
    require(msg.value > auction.highestBid, "Bid not high enough");
    require(msg.value >= minimumBid, "Bid below minimum bid");
    // Allow previous bids to be overridden
    uint256 newBidTotal = auction.bids[msg.sender] + msg.value;
    require(
        newBidTotal > auction.highestBid,
        "Total bid not high enough to become highest bidder"
    );
}
```
The problem is that the call can revert because of the first require statement that checks if the current msg.value > auction.highestBid. This could lead to the following scenario:
- User A bids 3 ETH.
- After that, User B bids 3.5 ETH, and now auction.highestBid = 3.5 ETH.
- User A wants to bid again and sends 1 ETH.
- The call reverts because of the first check - 1 ETH < 3.5 ETH.
- However, the newBidTotal will be 4 ETH which will be higher than auction.highestBid.
Thus, the function call will revert wrongly in step 4.

## Recommendation
Consider removing the first check and moving the second check after newBidTotal is calculated.
```solidity
// require(msg.value > auction.highestBid, "Bid not high enough");
// require(msg.value >= minimumBid, "Bid below minimum bid");
// Allow previous bids to be overridden
uint256 newBidTotal = auction.bids[msg.sender] + msg.value;
require(msg.value >= minimumBid, "Bid below minimum bid");
require(
    newBidTotal > auction.highestBid,
    "Total bid not high enough to become highest bidder"
);
```
