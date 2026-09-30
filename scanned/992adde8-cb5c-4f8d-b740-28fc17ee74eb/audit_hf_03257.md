# [M] OBU-3 | Unexpected Frozen Order

## Summary
Severity: Medium
Contest weight: 0.0666
Dataset id: 17876
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a limit order is executed with an invalid increasing/decreasing price range, the order reverts with a bespoke revert string–which results in the order getting frozen. But this is unexpected as all other order price-related errors simply revert and will be retried. This might lead to a poor execution of limit order types or a complete lack of execution of limit orders.

## Recommendation
Consider reverting in this case with a custom error that is handled similarly to the UNACCEPTABLE_PRICE_ERROR_KEY.
