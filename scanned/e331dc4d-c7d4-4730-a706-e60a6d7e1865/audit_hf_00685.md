# [M] M-06 | Missing Execute Order Function

## Summary
Severity: Medium
Contest weight: 0.1092
Dataset id: 2236
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During submitOffchainDelayedOrderWithTracking, a keeperFee is deducted from the position margin: _updatePositionMargin(messageSender, position, sizeDelta, ﬁllPrice, -int(keeperDeposit)); This fee is reserved for the caller of executeOffchainDelayedOrder that will settle the delayed order. However, according to the PerpsV2MarketDelayedExecution.sol contract: If this is called by the account holder the keeperFee is refunded into margin, otherwise it sent to the msg.sender. For the ETH Perp market, this keeper fee ranges from 1.05 to 100 sUSD. The LeveragedToken is the account holder in this case, but it does not contain any function to execute the delayed order, missing out on the fee refunds.

## Recommendation
Consider adding a public function to execute delayed orders and get the keeper fee back.
