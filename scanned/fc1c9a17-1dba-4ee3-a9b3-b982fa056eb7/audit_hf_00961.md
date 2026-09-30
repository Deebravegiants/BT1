# [M] totalOwed does not account for partial repayments

## Summary
Severity: Medium
Contest weight: 0.3965
Dataset id: 3022
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When claiming, the totalOwed calculation does not account for the newly introduced partial repayments.
```solidity
function claim(uint256 loanId) external override {
>
    uint256 totalOwed = terms.principal + interest;
```
Assume that the borrower had repaid part of the loan. Then, terms.principal would still be the full loan principal, but interest would be the remaining interest that has yet to be paid. As a result, the lender will pay more/less claim fees, depending on the intended fee for claiming a defaulted loan. For example, the lender could call repay() to repay his loan's currently owed interest. This would cause interest to become 0, therefore the lender would avoid paying claim fees on interest.

## Recommendation
If claim fees are meant to be calculated based on the entire loan's value (principal + total interest), add the amount of interest already paid to totalOwed:
```diff
- uint256 totalOwed = terms.principal + interest;
+ uint256 totalOwed = terms.principal + interest + data.interestAmountPaid
```
