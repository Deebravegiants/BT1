# [M] GLOBAL-2 | Saved Callback Keeper Grieﬁng

## Summary
Severity: Medium
Contest weight: 0.1101
Dataset id: 18886
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Saved callback contracts will be executed on liquidation and ADL orders which are entirely funded by the keeper/protocol without any remuneration from the user. Additionally, the saved callback contract will be given the maximum callback gas limit upon liquidation or ADL. This way malicious traders may grief the keeper by creating numerous positions that become liquidatable simply to force the keeper to expend the maximum callback gas limit. Notice that a malicious trader may also be able to directly extract value from the keeper with gas tokens upon a liquidation or ADL callback since this execution gas is subsidized by the protocol.

## Recommendation
Be aware of the potential for signiﬁcant uncovered gas expenditure. Consider implementing a mechanism to remunerate the keeper for excessive callback gas expenditure from the user’s remaining collateral in the case of liquidation and ADL orders.
