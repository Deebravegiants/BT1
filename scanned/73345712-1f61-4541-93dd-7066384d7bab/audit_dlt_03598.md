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
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-05-gondi-mitigation-findings/issues/34_
