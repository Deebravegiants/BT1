# [H] MKTU-5 | Fee Receiver Amount Included in Pool Value

## Summary
Severity: High
Contest weight: 0.1501
Dataset id: 18199
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The pool value is incremented by Precision.applyFactor(cache.totalBorrowingFees, cache.borrowingFeeReceiverFactor) which is the portion of borrowing fees going to the feeReceiver. Because this amount is paid to the feeReceiver rather than the pool, it should not be counted as part of the pool value. This misrepresents the pool’s accounting and incorrectly values the pool for deposits and withdrawals.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/MKTU_5.ts

## Recommendation
Include the portion of pending borrowing fees which will go into the pool rather than the portion allocated for the feeReceiver.
