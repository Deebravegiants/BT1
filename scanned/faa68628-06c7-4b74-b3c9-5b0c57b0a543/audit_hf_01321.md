# [H] H-4 Infinite Block Auction

## Summary
Severity: High
Contest weight: 0.0849
Dataset id: 6510
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The owner may not call resolveAuction (Auction.sol#L139): • to block lastBid of a user on the Auction contract and there is no mechanism to bypass that; • to prevent the pool's users from getting an insurance or bid after the auction; • to manipulate the market.

## Recommendation
We recommended allowing users to call resolveAuction if enough time has passed.
