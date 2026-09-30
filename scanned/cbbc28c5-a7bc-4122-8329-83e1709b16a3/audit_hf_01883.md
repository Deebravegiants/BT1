# [C] Attacker could force win auction by reverting on higher bids

## Summary
Severity: Critical
Contest weight: 0.2464
Dataset id: 10460
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol lets users create auctions and other users bet on them for a limited time. When a user creates a higher bid than the last, the last user's funds are returned. The problem is the way they are returned - the funds are directly sent back to the using transfer. The problem with this is that a malicious user could bid through a contract and set its receive and callback functions to revert when they receive ETH. That way the whole transaction would revert and it would NOT be able to outbid him. This gives an unfair advantage and is clearly wrong.
```solidity
uint256 lastBidPrice = auction.heighestBid;
// Transfer back to last bidder
payable(lastBidder).transfer(lastBidPrice);
```

## Recommendation
The most robust solution here would be to use pull over push - meaning to save the amount owned to a amount would do a perfect job.
