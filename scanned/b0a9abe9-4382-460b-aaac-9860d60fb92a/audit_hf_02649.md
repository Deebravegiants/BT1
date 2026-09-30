# [M] Circumvention of Checks in validateBorrow()

## Summary
Severity: Medium
Contest weight: 0.4270
Dataset id: 14361
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a user makes a borrow then repays it in the same transaction, the time difference will be zero as the block timestamp will not have changed between the calls to borrow() and repay(). Therefore users will not pay fees on a loan repaid in the same transaction since the interest accrued is zero, as it is based off time difference. The following check was added to validateBorrow() to prevent users from borrowing and repaying in the same transaction.
```solidity
require(
    lastBorrower == onBehalfOf &&
    lastBorrowTimestamp == uint40(block.timestamp),
    Errors.VL_SAME_BLOCK_BORROW_REPAY
);
```
Here the lastBorrowTimestamp is the timestamp of the most recent call to borrow() on this reserve by any user. It is possible to circumvent this check by using a temporary account to make a borrow before the original account repays the loan. Using two accounts contractA and contractB we may do the following:
1. contractA - borrow()
2. contractB - deposit() (with a very small amount)
3. contractB - borrow() (with an amount of minimal value e.g. 1 WEI)
4. contractA - repay()
The result is that contractA has borrowed and repaid within the same transaction, contractB will be left with a loan of minimal value.

## Recommendation
Consider storing a timestamp for each user (as opposed to one for all users) per reserve which records the last borrowed time. The trade-off is that it will require additional storage costs for the user the first time they make a loan on the reserve as they will have to make an SSTORE instruction on an empty storage slot (this is more expansive than making an SSTORE on a non zero storage slot).
Aave Protocol v2.0
