# [M] GLOBAL-3 | Unbounded Virtual Inventory Price Impact

## Summary
Severity: Medium
Contest weight: 0.1263
Dataset id: 18889
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no lower bound on how negative price impact can be during swaps or position orders due to the virtual inventory. In virtual inventories where there are many markets, it is possible to build up large imbalances over time as users may be incentivized with positive impact from their direct pool to make deposits or orders that ultimately increase the disparity in the virtual inventory. The resulting extreme disparity in the virtual inventory will lead to signiﬁcant negative impact without bound for unsuspecting users. The most likely outcome is that deposits and orders that would compute price impact from the virtual inventory will simply be cancelled due to their acceptable price or minimum amounts being unfulﬁllable.

## Recommendation
Consider implementing a lower bound on the magnitude of negative price impact that can be applied from the virtual inventory. Alternatively, consider creating separate price impact factors that can apply speciﬁcally to the virtual inventory calculations as the virtual inventory imbalances can be signiﬁcantly larger than normal markets.
