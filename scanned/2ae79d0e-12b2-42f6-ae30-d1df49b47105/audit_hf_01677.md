# [M] M-1 Lack of supply limit

## Summary
Severity: Medium
Contest weight: 0.0937
Dataset id: 9141
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To proﬁt from liquidations, liquidators must be able to sell collateral at a favorable price. However, selling a large amount of collateral may signiﬁcantly impact the selling price, rendering liquidation unproﬁtable and generating bad debt. A supply limit, conﬁgured to match market liquidity, could mitigate this issue. However, the supply limit has not been implemented yet. Although, the borrow limit is in place and may indirectly limit supply, it may not effectively address this issue due to substantial price ﬂuctuations often associated with large volumes of liquidations.

## Recommendation
We recommend implementing a supply limit and tracking its value as per market conditions.
