# [M] M-03 | _createLocks DoS

## Summary
Severity: Medium
Contest weight: 0.1437
Dataset id: 20723
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the processExpiredLocks function there is no requirement that the operator must process the oldest expired lock first. Therefore if an operator neglects to process expired locks for a user directly when they unlock it becomes possible for an operator to errantly or maliciously process the lock at the lastLockIndex before processing the other locks.
Depending on where the lastLockIndex is relative to the user’s locks array this can yield different outcomes:
In the following example lock A expired before lock B and lock B expired before lock C, lock C is the true last lock:
• lastLockIndex is 2
• The user’s locks array is [A, B, C]
• All locks are expired, the operator processes lock C first
• The user’s locks array is now [A, B], the lastLockIndex is still 2
However, 2 is an invalid index for the array and now the user cannot create a new lock as the _createLock function will revert with an array index out of bounds error.

## Recommendation
Consider requiring that the lock at the lastLockIndex may only be processed when there is only 1 item left in the locks array. Additionally, be sure to carefully process the correct locks on time.
