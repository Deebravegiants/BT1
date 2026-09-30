# [M] Borrowers can use RepaymentController.forceRepay() to temporarily prevent lenders from claiming collateral

## Summary
Severity: Medium
Contest weight: 0.4419
Dataset id: 3029
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a loan is past its due date, the Lender can claim the Borrower's collateral, which will end up with a call to LoanCore.claim().
```solidity
function claim(uint256 loanId, uint256 _amountFromLender)
external
override
onlyRole(REPAYER_ROLE)
nonReentrant
{
    LoanLibrary.LoanData memory data = loans[loanId];
    // Ensure valid initial loan state when claiming loan
    if (data.state != LoanLibrary.LoanState.Active) revert
    LC_InvalidState(data.state);
    // Check that loan has a noteReceipt of zero amount
    if (noteReceipts[loanId].amount != 0) revert
    LC_AwaitingWithdrawal(noteReceipts[loanId].amount);
}
```
Due to the noteReceipts[loanId].amount != 0 check above, the function will revert if the loan's note receipt has an outstanding balance that has not yet been claimed by the lender. A borrower can take advantage of this check to force claim() to revert:
• Lender calls claim().
• Borrower front-runs the lender's transaction and calls forceRepay() with 1 wei to create a note receipt.
• Lender's transaction is executed, but claim() reverts due to the check above. He has to call redeemNote() first before trying again.
As a result, the Borrower can easily prolong the loan for the cost of gas fees, although their loan duration is over. Note that there's no DOS for a fixed duration, but the borrower is actually incentivised to abuse this to delay the lender from claiming his collateral. He can also repeat this attack for as long as he wants.

## Recommendation
Consider removing the noteReceipts[loanId].amount != 0 check:
```diff
@@ -333,9 +333,6 @@ contract LoanCore is
// Ensure valid initial loan state when claiming loan
if (data.state != LoanLibrary.LoanState.Active) revert
LC_InvalidState(data.state);
// Check that loan has a noteReceipt of zero amount
if (noteReceipts[loanId].amount != 0) revert
LC_AwaitingWithdrawal(noteReceipts[loanId].amount);
// First check if the call is being made after the due date plus 10 min grace
period.
```
