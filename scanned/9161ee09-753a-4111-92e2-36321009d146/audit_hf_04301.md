# [M] M-09 | Refund gas limit is not accounted for

## Summary
Severity: Medium
Contest weight: 0.1238
Dataset id: 21450
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The payExecutionFee function refunds the leftover gas to the user **before** executing the external callback to refundExecutionFee. This gas refund doesn't take into account the fact that refundExecutionFee can use up to 500k gas. This will enable users to grief keepers, making their TX unproﬁtable. For Example:
1. User makes an order with 3m gas as execution fee.
2. Keeper executes that order with 3m gas (equal execution fee).
3. We reach payExecutionFee, where up to now 2m gas is used.
4. Keeper is payed 2m and the user is refunded 1m.
5. The refundExecutionFee triggers wasting 500k gas. In the current scenario the user only paid 2m gas for his order, but costed the keeper 2.5m gas.

## Proof of Concept
https://github.com/GuardianAudits/gmx-v2-1-team-2-pocs/tree/POC_UNRECORDED_GAS

## Recommendation
Increase EXECUTION_GAS_FEE_BASE_AMOUNT in order for adjustGasUsage to calculate the keeper gas properly.
