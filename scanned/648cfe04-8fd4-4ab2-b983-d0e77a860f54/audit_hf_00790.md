# [H] H-11 | Funds Can Be Frozen By Reordering Queues

## Summary
Severity: High
Contest weight: 0.1377
Dataset id: 2526
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The SuperPool owner has the capability to reorder deposit and withdrawal queues. However, there is a lack of duplicate entry check in the _reorderQueue function, which could potentially enable a malicious owner to freeze funds.
For instance:
• withdrawQueue = [1, 2, 3]
• A malicious owner reorders with indices [0, 0, 0]
• Resulting withdrawQueue = [1, 1, 1]
As a result, the funds deposited in pools 2 and 3 become unwithdrawable.

## Recommendation
It is recommended to implement a duplicate check within the function to prevent this issue from occurring. Verify the indexes param in the reorder queue functions contain all pool ids in the queue array.
