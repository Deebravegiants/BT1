# [H] MKTU-1 | Borrowing Fees Avoided Due To Skip

## Summary
Severity: High
Contest weight: 0.2342
Dataset id: 18874
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users who have accumulated a large amount of borrowing fees can avoid paying these fees as long as the cumulativeBorrowingFactor has not yet been incremented and skipBorrowingFeeForSmallerSide is enabled. Consider the following scenario: Long OI > Short OI. Trader A has a large long position that has accumulated a significant amount of borrowing fees. These borrowing fees have not been “solidified” by the update of any other long position. Therefore the cumulativeBorrowingFactor has not yet been incremented to account for Trader A’s accumulated borrowing fees since the last recorded cumulativeBorrowingFactorUpdatedAt for longs. Trader A opens another short position shifting the larger side to be the opposite of the first position. Trader A then closes the first position and pays 0 borrowing fees.

## Proof of Concept
https://github.com/GuardianAudits/GMX-6/blob/main/test/guardian/MKTU-1.ts

## Recommendation
Do not allow previously accumulated borrowing fees to be skipped in the event that a trader forces a side to have the smaller OI. This can be achieved by updating both the long and short borrowing fees upon position increase and decrease.
