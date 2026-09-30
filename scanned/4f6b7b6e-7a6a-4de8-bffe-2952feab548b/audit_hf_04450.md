# [H] H-01 | cancelDeposit Not Implemented In KeeperProxy

## Summary
Severity: High
Contest weight: 0.1147
Dataset id: 21941
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The cancelDeposit function has an onlyKeeper modiﬁer that restricts its execution to the
KeeperProxy contract.
However, the KeeperProxy does not implement the necessary functionality to call this function,
making it currently impossible to invoke.
The cancelDeposit function may be needed to cancel a reverting deposit to GMX, making it essential
for the system's proper operation.

## Recommendation
Implement a function in the KeeperProxy contract to call the cancelDeposit function.
