# [M] PENW-1 | DoS pendingWithdrawals

## Summary
Severity: Medium
Contest weight: 0.0930
Dataset id: 20589
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is no limit on the amount of pending withdrawals a user can have, nor is there a minimum amount of shares that ought to be redeemed per withdrawal. Therefore it can be economically viable to submit many withdrawals each with a single wei in order to expand the pendingWithdraws list for a malicious user. As a result third party contracts interacting with the PendingWithdraws.withdraws function can be DoS’d simply because the amount of gas required to load the pendingWithdraws list into memory is greater than the block gas limit.

## Recommendation
Consider adding either a limit on the amount of pending withdrawals a single user can have, or a minimum on the amount of shares necessary for a withdrawal to be queued or both.
