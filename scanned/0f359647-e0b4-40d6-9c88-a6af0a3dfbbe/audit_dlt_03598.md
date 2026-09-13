# [M] AuctionWithBuyoutLoanLiquidator lender get less interest

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-05-gondi-mitigation
Published: 2024-05-20
Source: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/34
Type: code-finding

## Details
# Lines of code

https://github.com/pixeldaogg/florida-contracts/blob/9f496f5b7cfcfe70fb60d1c3fa4cb7f4c3f66699/src/lib/AuctionWithBuyoutLoanLiquidator.sol#L100
https://github.com/pixeldaogg/florida-contracts/blob/9f496f5b7cfcfe70fb60d1c3fa4cb7f4c3f66699/src/lib/LiquidationDistributor.sol#L60


# Vulnerability details

## Vulnerability details
https://github.com/pixeldaogg/florida-contracts/pull/371

this PR Changed to loan end time instead of current timestamp

In order to resolve the issue of liquidation ,`LiquidationDistributor.distribute()` may break maxSeniorRepayment's expectations

There are two issues
### first
this PR Also modified another contract `AuctionWithBuyoutLoanLiquidator.sol`

```diff
contract AuctionWithBuyoutLoanLiquidator is AuctionLoanLiquidator {
...

+       uint256 loanEndTime = _loan.startTime + _loan.duration;
        uint256 totalOwed;
        for (uint256 i; i < _loan.tranche.length;) {
            if (i != largestTrancheIdx) {
                IMultiSourceLoan.Tranche calldata thisTranche = _loan.tranche[i];
                uint256 owed = thisTranche.principalAmount + thisTranche.accruedInterest
-                   + thisTranche.principalAmount.getInterest(thisTranche.aprBps, block.timestamp - thisTranche.startTime);
+                   + thisTranche.principalAmount.getInterest(thisTranche.aprBps, loanEndTime - thisTranche.startTime);
                totalOwed += owed;
                asset.safeTransferFrom(msg.sender, thisTranche.lender, owed);

                if (getLoanManagerRegistry.isLoanManager(thisTranche.lender)) {
                    LoanManager(thisTranche.lender).loanLiquidation(
                        thisTranche.loanId,
                        thisTranche.principalAmount,
                        thisTranche.aprBps,
                        thisTranche.accruedInterest,
                        _loan.protocolFee,
                        owed,
                        thisTranche.startTime
                    );
                }
            }

```

The change to `AuctionWithBuyoutLoanLiquidator` does not make sense, the interest should still be calculated using the current time, because:

1. `AuctionWithBuyoutLoanLiquidator` is a user-initiated repayment and requires full payment of the amount owed, unlike a bidding auction where there is a shortfall in the amount owed.
So there is no "maxSeniorRepayment" problem. 

2. the user has 4 days to consider `MAX_TIME_FOR_MAIN_LENDER_TO_BUY = 4 days`, during this time, `lender` has not received the payment, and should calculate the interest.
(Users can maliciously delay the repayment, anyway, when to repay, the repayment amount is the same)

### second
`LiquidationDistributor` should only use `loan end time` if the reimbursement amount is insufficient.
It makes more sense to use `block.timestamp` when the amount is enough.
Since each `Tranche` has different `aprBps`, it would make more sense to calculate the interest at the `current time` and allocate the excess amount in proportion to the last `owed` amount `excess = _proceeds - _totalOwed;`.

## Impact
The "lender" is missing 4 days of interest.
The purchaser can postpone the purchase without loss.

## Recommended Mitigation
`AuctionWithBuyoutLoanLiquidator.sol` still using `block.timestamp`
`LiquidationDistributor.sol` Repayment is first made on the basis of `loan end time` and if there are funds remaining, the percentage of arrears is calculated on the basis of `block.timestamp' and the excess is distributed proportionately.




## Assessed type

Context
