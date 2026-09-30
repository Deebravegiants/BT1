# [M] NFT can be stuck in the contract

## Summary
Severity: Medium
Contest weight: 0.0594
Dataset id: 10490
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol lets users create auctions where they can sell their NFTs. Sellers can set minimum bid price
auction start and end times. Sellers can also cancel their auctions, but only if it is before the auction start
time. However, if no one participates in the auction and it has ended the last/highest bidder would be the 0

## Recommendation
Set the highest bidder to the creator when no bids are received and transfer the NFT back to them at auction end.
