# [M] Stale feeSnapshot is used when rolling over a loan

## Summary
Severity: Medium
Contest weight: 0.4190
Dataset id: 3034
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When rolling over a loan, instead of fetching the most recent fees through FeeController.getOriginationFeeAmounts() the function assigns the new loan fees by reusing data.feeSnapshot that was taken when the previous loan was created. This means that even if the protocol's default, interest and principal fees were updated, the new loan created by rollover() would still use old fee values.
```solidity
function rollover(
    uint256 oldLoanId,
    address oldLender,
    address borrower,
    address lender,
    LoanLibrary.LoanTerms calldata terms,
    uint256 _settledAmount,
    uint256 _amountToOldLender,
    uint256 _amountToLender,
    uint256 _amountToBorrower,
    uint256 _interestAmount
) external override whenNotPaused onlyRole(ORIGINATOR_ROLE) nonReentrant returns
(uint256 newLoanId) {
>
    LoanLibrary.LoanData storage data = loans[oldLoanId];
    loans[newLoanId] = LoanLibrary.LoanData({
        state: LoanLibrary.LoanState.Active,
        startDate: uint64(block.timestamp),
        lastAccrualTimestamp: uint64(block.timestamp),
        terms: terms,
>
        feeSnapshot: data.feeSnapshot,
        balance: terms.principal,
        interestAmountPaid: 0
    });
```

## Recommendation
When rolling over a loan, the new loan's feeSnapshot should be fetched using FeeController.getOriginationFeeAmounts().
