# [M] Interest paid for non perpetual offer not properly accounted during loan extension and repayment

## Summary
Severity: Medium
Contest weight: 0.6789
Dataset id: 1843
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a borrower call extendLoan() to extend a loan to the max deadline, interest is accrued to the lender up until the time the loan is extended and the lender's interestPaid is updated as well for accounting purpose when calculating the interest with calculateInterestToPay()
ontracts/contracts/DebitaV3Loan.sol#L655-L65
ontracts/contracts/DebitaV3Loan.sol#L237C1-L241C14
As shown below interest is accrued and interestPaid is also accrued correctly
File: DebitaV3Loan.sol
```solidity
655: } else {
656:     loanData._acceptedOffers[i].interestToClaim +=
657:         interestOfUsedTime -
658:         interestToPayToDebita;
659: }
660: loanData._acceptedOffers[i].interestPaid += interestOfUsedTime;
```
The problem is that when a borrower extends a loan and later repays the loan at the end of the maxDeadline that the loan was extended to, the unpaid interest is used to overwrite the previously accrued interest (as shown on L238 below) thus leading to a loss of interest to the borrower
File: DebitaV3Loan.sol
```solidity
186: function payDebt(uint[] memory indexes) public nonReentrant {
187:     IOwnerships ownershipContract = IOwnerships(s_OwnershipContract);
////SNIP
237: } else {
238:     loanData._acceptedOffers[index].interestToClaim =
239:         interest -
240:         feeOnInterest;
241: }
```
Internal pre-conditions
External pre-conditions
Attack Path
This leads to a loss of interest for the lender

## Recommendation
Modify the payDebt() function as shown below
File: DebitaV3Loan.sol
```solidity
186: function payDebt(uint[] memory indexes) public nonReentrant {
187:     IOwnerships ownershipContract = IOwnerships(s_OwnershipContract);
////SNIP
237: } else {
-238:     loanData._acceptedOffers[index].interestToClaim =
+238:     loanData._acceptedOffers[index].interestToClaim +=
239:         interest -
240:         feeOnInterest;
241: }
```
