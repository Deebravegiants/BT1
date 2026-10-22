# [H] `_baseLoanChecks

## Summary
Severity: High
Contest weight: 0.3257
Dataset id: 21165
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
`_baseLoanChecks()` is used to check whether Loan has expired:
```
    function _baseLoanChecks(uint256 _loanId, Loan memory _loan) private view {
        if (_loan.hash() != _loans[_loanId]) {
            revert InvalidLoanError(_loanId);
        }
        if (_loan.startTime + _loan.duration < block.timestamp) {
            revert LoanExpiredError();
        }
    }
```
The expiration checks in liquidation are as follows:
```
    function _liquidateLoan(uint256 _loanId, IMultiSourceLoan.Loan calldata _loan, bool _canClaim)
        internal
        returns (bool liquidated, bytes memory liquidation)
    {
...

        uint256 expirationTime = _loan.startTime + _loan.duration;
        if (expirationTime > block.timestamp) {
            revert LoanNotDueError(expirationTime);
        }
```
This way, both checks pass when `block.timestamp == _loan.startTime + _loan.duration`.

This leads to the problem that a malicious attacker can perform the following steps when `block.timestamp == _loan.startTime + _loan.duration`:

1. Alice calls `liquidateLoan` (`loandId` = 1) -> success.

   * `LoanLiquidator` generates an auction.
   * `_loans[loandId = 1]` is still valid , and will only be cleared when the auction is over.
2. Alice call `addNewTranche` (`loandId` = 1) -> success.

   * `_baseLoanChecks` (`loandId` = 1) will pass.
   * delete `_loans[1]`;
   * `_loans[2] = newLoan.hash()`.
3. Bidding ends, call `loanLiquidated(loandId = 1)` will fail , because `_loans[1]` has been cleared.

## Recommendation
```
function _baseLoanChecks(uint256 _loanId, Loan memory _loan) private view {
        if (_loan.hash() != _loans[_loanId]) {
            revert InvalidLoanError(_loanId);
        }
       if (_loan.startTime + _loan.duration <= block.timestamp) {
            revert LoanExpiredError();
        }
    }
```
