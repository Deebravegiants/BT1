# [M] `Auction.sol#settleAuction`

## Summary
Severity: Medium
Contest weight: 0.4203
Dataset id: 907
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The `newRatio` that determines `tokensNeeded` to settle the auction is calculated based on `auctionMultiplier`, `bondTimestamp - auctionStart` and `auctionDecrement`.

```solidity
uint256 a = factory.auctionMultiplier() * basket.ibRatio();
uint256 b = (bondTimestamp - auctionStart) * BASE / factory.auctionDecrement();
uint256 newRatio = a - b;
```

However, if an auction is bonded late (`bondTimestamp - auctionStart` is a large number), and/or the `auctionMultiplier` is small enough, and/or the `auctionDecrement` is small enough, that makes `b` to be greater than `a`, so that `uint256 newRatio = a - b;` will revert on underflow.

This might seem to be an edge case issue, but considering that a rebalance auction of a bag of shitcoin to high-value tokens might just end up being bonded at the last minute, with a `newRatio` near zero. When we take the time between the bonder submits the transaction and it got packed into a block, it’s quite possible that the final `bondTimestamp` gets large enough to revert `a - b`.

## Recommendation
Calculate and require `newRatio > 0` in `bondForRebalance()`, or limit the max value of decrement and make sure newRatio always > 0 in `settleAuction()`.

Finding is valid, there are cases that can cause a - b to revert

The finding is reliant on external condition (multiplier being low and / or bonding late) as such I believe this to be a medium severity finding.

Note for the sponsor: The cause for reverts should get clearer with time (as people use the protocol), you definitely want to model these revert behaviour to avoid edge cases that will make funds stuck
