# [H] H-13 | DoS In _supplyToPools If One Deposit Fails

## Summary
Severity: High
Contest weight: 0.1109
Dataset id: 2528
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Every deposit call could fail if the BasePool is paused, or if the cap in the BasePool is reached.
As this call is not wrapped into a try-catch block, the transaction will revert and therefore the user is not able to deposit into the other pools of the queue. For example, if the first BasePool in the queue is paused the whole SuperPool deposit function is not usable.

## Recommendation
Wrap the deposit call into a try-catch block as it is done with withdraws.
