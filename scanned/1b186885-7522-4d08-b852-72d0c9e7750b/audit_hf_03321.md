# [H] MKTU-7 | Total Borrowing Fees Outdated

## Summary
Severity: High
Contest weight: 0.1788
Dataset id: 18172
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The getTotalBorrowingFees function, which returns the pending borrowing fees, is out of date as it uses an outdated cumulativeBorrowingFactor rather than getting the updated factor with getNextCumulativeBorrowingFactor. As a result, LPs who withdraw will have their market tokens worth less than they should be as the pending fees aren’t reflected in the pool value. Additionally, this introduces the opportunity for arbitrages that take advantage of the stepwise increase in borrowingFees by forcing an update with a trivial MarketIncrease order.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/MKTU_7.ts

## Recommendation
Use getNextCumulativeBorrowingFactor instead of getCumulativeBorrowingFactor to get the latest pending borrowing fees.
