# [H] Borrower can abuse partial repayments to deny Lender from redeeming repaid funds.

## Summary
Severity: High
Contest weight: 0.8014
Dataset id: 3009
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Borrowers can call forceRepay() instead of repay(), this will not transfer the repaid amount to the lender directly but is held in a noteReceipts mapping. Lenders can then call redeemNote() to claim the repaid amount, however, they still need to own their PromissoryNote to prove ownership.

```solidity
function redeemNote(
    uint256 loanId,
    uint256 _amountFromLender,
    address to
) external override onlyRole(REPAYER_ROLE) nonReentrant {
    // Get owner of the LenderNote
    address lender = lenderNote.ownerOf(loanId);
    // if the loan has been completely repaid and no more repayments are expected
    if (loans[loanId].state == LoanLibrary.LoanState.Repaid) {
        // delete the receipt
        delete noteReceipts[loanId];
        // Burn ONLY the LenderNote
        lenderNote.burn(loanId);
    } else {
        // zero out the total amount owed in the receipt
        noteReceipts[loanId].amount = 0;
    }
}
```

However, since repay() doesn't check if the loan has an existing note receipt, a borrower can abuse partial repayment and note receipts to make the lender unable to claim the repaid principal + interest:
- Borrower calls forceRepay() to repay principal + interest - 1 wei. The repaid amount is held in a note receipt.
- Borrower calls repay() to repay the last 1 wei. This will burn the lender note since loans[loanId].state changes to LoanState.Repaid
- Lender can't call redeemNote() anymore since they no longer hold the lender note, so they can't ever claim the repayment.

Borrowers can also call rollover() in place of repay() to achieve the same impact, since rollover() also burns the lender note.

```solidity
function repay(
    uint256 loanId,
    address payer,
    uint256 _amountToLender,
    uint256 _interestAmount,
    uint256 _paymentToPrincipal
) external override onlyRole(REPAYER_ROLE) nonReentrant {
    if (loans[loanId].state == LoanLibrary.LoanState.Repaid) {
        // if loan is completely repaid
        // burn both notes
        _burnLoanNotes(loanId);
        // redistribute collateral and emit event
        IERC721(data.terms.collateralAddress).safeTransferFrom(address(this), borrower, data.terms.collateralId);
        emit LoanRepaid(loanId);
    }
}
```

## Recommendation
A potential would be to only burn the lender note when the loan's note receipt has no more balance:

```diff
@@ -923,7 +922,10 @@ contract LoanCore is
function _burnLoanNotes(uint256 loanId) internal {
    lenderNote.burn(loanId);
+
    if (noteReceipts[loanId].amount == 0) {
+
        lenderNote.burn(loanId);
+
    }
+
    borrowerNote.burn(loanId);
}
```

This way all functionality remains the same, except that if the lender hasn't called redeemNote() and a full repayment is made using repay() or rollover(), he will still have the ability to call redeemNote() afterwards.

Note that if the fix for - ”Borrower can abuse RepaymentController.forceRepay() to temporary DOS a Lender from claiming collateral” - is to remove the check, you would have to burn lender notes in redeemNote() after claim() as well:

LoanCore.sol#L404-L405
```diff
// if the loan has been completely repaid and no more repayments are expected
- if (loans[loanId].state == LoanLibrary.LoanState.Repaid) {
+ LoanLibrary.LoanState state = loans[loanId].state;
+ if (state == LoanLibrary.LoanState.Repaid || state == LoanLibrary.LoanState.Defaulted) {
```
