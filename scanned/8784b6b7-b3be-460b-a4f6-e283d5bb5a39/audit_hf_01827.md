# [M] M-4 Request cancelling can be DoSed

## Summary
Severity: Medium
Contest weight: 0.0820
Dataset id: 10171
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A user that wants to receive unstaked ETH without losses can DoS cancelUnfinalizedRequests UnstakeRequestsManager.sol#L240 by simply creating dozens of unstake requests. This will require only additional gas costs for sending transactions, all METH that will be blocked on the UnstakeManager during DoS will be returned to the user. Additional unstake requests will require admin to remove more requests than they expected, leading to out-of-gas cases or not all requests will be removed.

## Recommendation
We recommend calling cancelUnfinalizedRequests only via private pools so users cannot front-run this call.
