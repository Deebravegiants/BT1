# [M] M-15 | Inadequate Estimated Liquidation Costs

## Summary
Severity: Medium
Contest weight: 0.1377
Dataset id: 2273
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the getLiquidationKeeperFee function the resulting estimated keeper fee is restricted to the maxKeeperFeeUsd. However when estimating the initial margin and maintenance margin values necessary for a position the estimated keeper fee may apply to multiple liquidatePosition transactions. Therefore a single maxKeeperFeeUsd is insuﬃcient to cover these multiple transactions. As a result, positions which would require multiple liquidatePosition calls are not required to hold the estimated keeper fee for each transaction. It is unlikely that positions large enough to require multiple liquidatePosition calls would not be able to cover the keeper fees due to increased maintenance margin requirements. However out of an abundance of caution, the estimated keeper fees should allow multiple liquidate position calls to be accounted for.

## Recommendation
Consider multiplying the globalConﬁg.maxKeeperFeeUsd by the iterations amount. This way liquidation keeper fee estimations for MM and IM will include the fees necessary for multiple high cost liquidatePosition calls. return MathUtil.min(liquidationFeeInUsd * iterations, globalConﬁg.maxKeeperFeeUsd * iterations);
