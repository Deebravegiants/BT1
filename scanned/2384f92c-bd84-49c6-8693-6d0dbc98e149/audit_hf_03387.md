# [M] MKTU-3 | Pending Borrowing Fees Brick Withdrawals

## Summary
Severity: Medium
Contest weight: 0.0833
Dataset id: 18495
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is possible for user’s withdrawals to revert because the pending borrowing fees are attributed to
the user’s withdrawal but have not yet been added to the poolAmount.
In cases where there is a significant amount of unpaid borrowing fees this can become a non-trivial
issue for users attempting to withdraw.

## Proof of Concept
https://github.com/GuardianAudits/GMX-4/blob/033061d771f2b327c2fbd4ab59e960109ee85dc2/test/guardian/PoCs.ts#L520

## Recommendation
Consider allowing a separate claiming process for borrowing fees, or implementing a pathway for
regular position updates to pay the pending borrowing fees.
