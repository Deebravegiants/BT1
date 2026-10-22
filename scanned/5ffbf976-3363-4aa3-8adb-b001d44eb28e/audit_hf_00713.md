# [M] M-07 | Debt With Zero Collateral Is Unliquidateable

## Summary
Severity: Medium
Contest weight: 0.1275
Dataset id: 2264
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
An account that has debt but no collateral and no position cannot be liquidated. This is due to a check within the liquidateMarginOnly function which reverts with CannotLiquidateMargin in the case there is no collateral. This would effectively lock the loss in the system and never recognize it which would mean credit capacity would be overstated since the total debtUSD is added back to the ﬁnal calculation. The severity is reduced due to the diﬃculty since we were unable to ﬁnd a way to put an account in this state with any signiﬁcant debt value. Currently the only identiﬁed means to achieve such a state is due to rounding error when splitting a position, such that a position can be left with 0 collateral and a few wei of debt. However, depending on how M-07 is resolved, this may become more likely and impactful in the future.

## Recommendation
Consider removing the constraint that an account cannot have zero collateral when calling liquidateMarginOnly.
