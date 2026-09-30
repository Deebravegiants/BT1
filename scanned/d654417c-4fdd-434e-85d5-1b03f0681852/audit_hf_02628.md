# [C] Liquidator Can Bid With Insufficient Cash

## Summary
Severity: Critical
Contest weight: 0.1462
Dataset id: 14202
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When executeBid() performs _symmetricManagerAdjustment() on the cash asset of the bidder, there is no check that the bidder’s cash balance remains positive after the adjustment. This could result in a negative cash balance after the bid.
The impact is that an attacker can bid on an auction with an insufficient cash balance, and let their cash balance go negative. The account being liquidated would still get an increase to their cash balance. This is eﬀectively printing cash which could make the protocol insolvent.

## Recommendation
The testing team recommends performing risk checks after liquidation bids are executed.
