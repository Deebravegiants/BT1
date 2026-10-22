# [M] Unknown Repayment Amount

## Summary
Severity: Medium
Source: https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/CErc20.sol#L86
Type: audit-issue

## Details
To repay an ERC20 loan, a borrower can call [repayBorrow](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/CErc20.sol#L86) or [repayBorrowBehalf](https://github.com/compound-finance/compound-protocol/blob/f385d71983ae5c5799faae9b2dfea43e5cf75262/contracts/CErc20.sol#L96) with a specified amount to repay.

However, they accrue interest in every block, which means if they specify the value of the loan at a particular block, their loan will be slightly higher in a future block when the transaction is confirmed and they will end up leaving part of the loan unpaid.

On the other hand, they could set the repay amount to `uint256(-1)`, which is used as a signal to mean “pay the whole loan”. This prevents the user from setting an upper bound on how much to pay. It is also particularly vulnerable in the case where an address is repaying on behalf of another address, since the borrower could front-run the transaction and borrow additional funds (up to the amount that the message sender has authorized the `CToken` contract to spend), which would also be repaid in the same transaction.

Consider treating the specified repayment amount as an upper bound, where the transaction repays the minimum of that value and the size of the loan.
