# [H] Rounding of sell amounts in RebalancingLib can make rebalancing stuck

## Summary
Severity: High
Contest weight: 0.1059
Dataset id: 13531
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The RebalancingLib generates orders for the rebalancing and reserve rebalancing. It is important that orders with localChain != destinationChain and zero sellAmount do not increment incomingOrders. This is because on the local chain, such orders will be skipped in OrderLib.set().

## Recommendation
There exist two instances of this issue in the RebalancingLib. In RebalancingLib.previewReserveRebalancingOrders(), reserveAmount > 0 does not imply orderSellAmount > 0 and so the check needs to replace reserveAmount with orderSellAmount.
