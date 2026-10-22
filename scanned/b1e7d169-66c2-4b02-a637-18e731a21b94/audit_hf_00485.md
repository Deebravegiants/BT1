# [M] Not updating state before mak-

## Summary
Severity: Medium
Contest weight: 0.4592
Dataset id: 1927
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Not updating state before making custom external call can cause borrower's to loose assets due to re-entrancy
The details of the repayment is updated only after the external call to the loanRepayment Listener is made
ontracts/TellerV2.sol#L865-L870
```solidity
function _repayLoan(
    uint256 _bidId,
    Payment memory _payment,
    uint256 _owedAmount,
    bool _shouldWithdrawCollateral
) internal virtual {
    ....
    _sendOrEscrowFunds(_bidId, _payment); //send or escrow the funds
    // update our mappings
    bid.loanDetails.totalRepaid.principal += _payment.principal;
    bid.loanDetails.totalRepaid.interest += _payment.interest;
    bid.loanDetails.lastRepaidTimestamp = uint32(block.timestamp);
}

function _sendOrEscrowFunds(uint256 _bidId, Payment memory _payment) internal virtual {
    ....
    address loanRepaymentListener = repaymentListenerForBid[_bidId];
    if (loanRepaymentListener != address(0)) {
        require(gasleft() >= 80000, "NR gas");
        //fixes the 63/64 remaining issue
        try
            ILoanRepaymentListener(loanRepaymentListener).repayLoanCallback{
                gas: 80000
            }( //limit gas costs to prevent lender preventing repayments
                _bidId,
                _msgSenderForMarket(bid.marketplaceId),
                _payment.principal,
                _payment.interest
            )
        {} catch {}
    }
}
```
This allows a malicious lender to reenter the TellerV2 contract and invoke lenderCloseLo an seizing the collateral of the borrower as well if the loan is currently defaulted
Internal pre-conditions
1. The repayment should be made after defaultTimestamp has passed
External pre-conditions
Attack Path
1. Defaulting timestmap of loan has passed
2. Borrower does a repayment of 100 which is transferred to the lender. Following this .repayLoanCallback is called
3. Lender reenters via the loanRepaymentListener and invokes the lenderCloseLoan function further seizing the collateral of the borrower
4. Borrower looses both the repayment amount and the collateral
Borrower will loose repayment amount and also the collateral

## Recommendation
Update the state before the loanRepaymentListener call is made
