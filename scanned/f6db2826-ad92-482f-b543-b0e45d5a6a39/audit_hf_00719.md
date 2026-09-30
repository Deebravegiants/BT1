# [M] M-12 | Unexpected Liquidations Caused By Block.basefee

## Summary
Severity: Medium
Contest weight: 0.1216
Dataset id: 2270
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To ensure that liquidators are adequately compensated for liquidating unhealthy positions, the liquidation fee is partially based on block.basefee. This differs from most liquidation functionality that does not base the fee on network activity. The issue here is that users may get liquidated due to factors beyond their position's actual health. A seemingly healthy position could become unhealthy simply because of an increase in network activity. The block.basefee can increase by as much as 12.5% from one block to another. This could potentially incentivize attackers to manipulate block.basefee, or it could occur naturally as the network experiences spikes in activity. All of this would be unexpected for users and could result in a loss of collateral for those affected.

## Recommendation
Consider implementing a ﬂat liquidation fee. Alternatively, document to users that network activity can impact their liquidation status.
