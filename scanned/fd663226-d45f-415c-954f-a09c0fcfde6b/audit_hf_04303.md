# [C] C-02 | LimitSwaps Cannot Execute After Request Expiration

## Summary
Severity: Critical
Contest weight: 0.0988
Dataset id: 21452
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When handling swap orders, the validation for the requestExpirationPeriod is meant to only be applied to MarketSwaps. Since it is applied to both swap types, it will revert for nearly all LimitSwaps. This will occur because the majority of LimitSwaps will not be eligible to be executed until a later time has passed than the REQUEST_EXPIRATION_TIME.

## Recommendation
Only perform this veriﬁcation for MarketSwaps.
