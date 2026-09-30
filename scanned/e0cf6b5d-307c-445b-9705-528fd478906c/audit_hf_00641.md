# [M] M-03 | Borrow Rate Gaming

## Summary
Severity: Medium
Contest weight: 0.1210
Dataset id: 2158
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The currentBorrowBalance and trackBorrow functions accrue interest and therefore update the totalBorrows which would influence the utilizationRate and therefore the borrowRate. However, they do not have the _update modifier and therefore do not update the borrowRate. Therefore the system potentially deals with a stale borrowRate and the lenders receive less yield than they should. Furthermore, the system allows for interest gaming, since calling sync() every second will provide a different debt accumulated than calling sync() once over the same timespans. For example, with a decreasing _kinkBorrowRate every sync the borrow rates will also decrease and cause less to be repaid over the borrow’s lifetime, which in turn is less yield for lenders.

## Recommendation
Add the _update modifier to the currentBorrowBalance and trackBorrow functions. Furthermore, re-consider if the system show allow for varying sync times to lead to different costs on users.
