# [M] M-01 | makeExternalCalls Unexpected Funds Receiver

## Summary
Severity: Medium
Contest weight: 0.1127
Dataset id: 21417
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When makeExternalCalls is used a batch of target contracts are called. This is used to allow users to interact with external contracts to perform a variety of operations. After the contracts are called makeExternalCalls will loop through an array of refund tokens and send each token to a desired recipient. The issue is that in cases where two recipients are expected to receive the same token the first recipient will receive 100% of the tokens while the second recipient will receive nothing. This is because the amount sent to each recipient is based on the balanceOf for the specific token, which ensures the entire balance will be used on the first recipient. Resulting in some address not receiving their expected funds.

## Recommendation
Iterate through refundToken and check that there are no duplicate addresses in the array.
