# [H] refinanceFromLoanExecutionData() Reusing borrower's signature to steal funds

## Summary
Severity: High
Chain: Smart contract
Component: 2024-05-gondi-mitigation
Published: 2024-05-20
Source: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/39
Type: code-finding

## Details
# Lines of code

https://github.com/pixeldaogg/florida-contracts/blob/b83b37bbe69325b12e3b8119dfd86eb86f16fc73/src/lib/loans/MultiSourceLoan.sol#L320


# Vulnerability details

## Vulnerability details
in `refinanceFromLoanExecutionData()`

The `LoanExecutionData` signature of `borrower` is reusable (since there are no nonces, as long as it doesn't expire)

Suppose `loanOffer.fee =100`.
Then each time `refinanceFromLoanExecutionData()` is executed the funds flow as follows.
1. lender pay = loanOffer.principalAmount - loanOffer.fee
2. borrower repay = loanOffer.principalAmount

So for each execution, `lender` receives a `loanOffer.fee` difference.

( loanOffer.principalAmount - (loanOffer.principalAmount - loanOffer.fee))

This way a malicious `lender` can monitor `emitLoan()` to reuse the signature of the `borrower` to steal funds
Example.
1. bob signs a borrower's `LoanExecutionData` and executes `emitLoan()`. loan : {fee = 1% , lender = alice}
2. Malicious user alice executes `refinanceFromLoanExecutionData(loan)` after `bob`'s transaction, using the signature that `bob` just signed.
3. every time `refinanceFromLoanExecutionData(loan)` is executed, alice gets an extra `fee = 1%`.

## POC
The following code demonstrates the reuse of the `emitLoan()` signature to steal funds.

add to MultiSourceLoan.t.sol
```solidity
    function testReuseBorrowSign() public {
        uint256 privateKey = 100;
        address otherBorrower = vm.addr(privateKey);
        uint256 otherToken = collateralTokenId + 1;

        IMultiSourceLoan.LoanOffer memory loanOffer =
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/39_
