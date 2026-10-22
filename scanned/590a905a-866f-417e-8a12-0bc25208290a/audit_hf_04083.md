# [M] AITB-1 | Unbounded Execution Fee For Deposits and Withdrawals

## Summary
Severity: Medium
Contest weight: 0.0817
Dataset id: 20536
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
After deposit or withdrawal execution, the excess execution fee is refunded. However, this refund is
inaccessible by the user initiating the wrapping or unwrapping, but rather held by the Dolomite
Margin owner.
This can potentially cause asset loss as there are no limits on how much msg.value a user can
forward as the execution fee. A user may prefer to ﬁrst deposit for GM directly through GMX, as they
are assured that they don’t lose native tokens unnecessarily.

## Recommendation
If the attribution of gas refunds is too constrictive with current size limits, consider bounding how
much msg.value a user forwards for GMX execution.
