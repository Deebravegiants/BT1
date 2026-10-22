# [M] M-05 | Excess executionFee Not Refunded

## Summary
Severity: Medium
Contest weight: 0.0751
Dataset id: 21959
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In withdraw(), _payExecutionFee() is called, which validates the msg.value is large enough to cover GMX’s execution cost. However, if a user goes to withdraw when there are no open positions, there will be no calls made to GMX. Additionally, when calls to GMX are made, any excess execution fee refund by GMX is not returned to the user. This can occur when a user calls deposit() or withdraw().

## Recommendation
Move the _payExecutionFee call into the curPositionKey != bytes32(0) case for withdrawing. Additionally, implement functionality to refund excess GMX execution fees to the creator of the deposit or withdrawal.
