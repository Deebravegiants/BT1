# [H] H-04 | Reallocating Can Freeze Funds

## Summary
Severity: High
Contest weight: 0.1716
Dataset id: 2547
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the reallocate function it is not checked if the given pools to deposit to are part of the deposit/withdraw queue.
Therefore malicious SuperPool owners can deposit funds into a pool that is not in the queue, which will freeze funds for the users of the SuperPool.
The owner could then spread on social media that users need to pay X amount of funds to unfreeze it (this could be even done with a contract).
When the users pay the amount, the owner can unfreeze the funds by adding the new pool to the queue or reallocating the funds back to the original pool.

## Recommendation
Add a check to see if the pools are part of the deposit/withdraw queue.
