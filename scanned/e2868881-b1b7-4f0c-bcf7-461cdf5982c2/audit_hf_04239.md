# [H] Function `settleWithBuyout`

## Summary
Severity: High
Contest weight: 0.7983
Dataset id: 21154
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Lenders in the Gondi protocol could be EOA and Gondi Pool. Gondi Pool, an ERC4626, allows anyone to deposit funds and earn yield from lending on Gondi. Gondi Pool implemented the `LoanManager` interfaces, which include the `validateOffer()`, `loanRepayment()`, and `loanLiquidation()` functions. The functions `loanRepayment()` and `loanLiquidation()` are called when a borrower repays the loan or the loan is liquidated, i.e., when the Pool receives funds back from `MultiSourceLoan`. Both functions is used to update the queue accounting and the outstanding values of the Pool.
```solidity
ERC20 asset = ERC20(_auction.asset); 
uint256 totalOwed;
// @audit Repay lender but not call LoanManager.loanLiquidation()
for (uint256 i; i < _loan.tranche.length;) {
    if (i != largestTrancheIdx) { 
        IMultiSourceLoan.Tranche calldata thisTranche = _loan.tranche[i];
        uint256 owed = thisTranche.principalAmount + thisTranche.accruedInterest
            + thisTranche.principalAmount.getInterest(thisTranche.aprBps, block.timestamp - thisTranche.startTime);
        totalOwed += owed; 
        asset.safeTransferFrom(msg.sender, thisTranche.lender, owed);
    }
    unchecked {
        ++i;
    }
}
IMultiSourceLoan(_auction.loanAddress).loanLiquidated(_auction.loanId, _loan);
```
In the `settleWithBuyout()` function, the main lender buys out the loan by repaying all other lenders directly. However, `loanLiquidation()` is not called, leading to incorrect accounting in the Pool.

## Proof of Concept
The `loanLiquidation()` function handles accounting in the pool.
```solidity
function loanLiquidation(
    ...
) external override onlyAcceptedCallers {
    uint256 netApr = _netApr(_apr, _protocolFee);
    uint256 interestEarned = _principalAmount.getInterest(netApr, block.timestamp - _startTime);
    uint256 fees = IFeeManager(getFeeManager).processFees(_received, 0);
    getCollectedFees += fees;
    _loanTermination(msg.sender, _loanId, _principalAmount, netApr, interestEarned, _received - fees);
}
```

## Recommendation
Consider checking and calling `loanLiquidation()` in `settleWithBuyout()` to ensure accurate accounting in the pool.

Changing interest paid to use the end of the loan (this appears in another issue since this delta in time otherwise breaks the `maxSeniorRepayment` concept).

Added `loanLiquidation` call.
