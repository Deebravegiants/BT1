# [M] LoanCore.rollover() doesnt distribute fees to the old loans affiliate

## Summary
Severity: Medium
Contest weight: 0.6650
Dataset id: 3028
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
LoanCore.rollover() distributes fees to only the new loan's affiliateCode and doesn't use old loan's affiliateCode:
```solidity
// Make sure split goes to affiliate code from _new_ terms
(uint256 protocolFee, uint256 affiliateFee, address affiliate) =
_getAffiliateSplit(feesEarned, terms.affiliateCode);
```
Since the new loan's affiliateCode can be different from the old loan, the old loan's affiliate will lose out on interest fees when the loan is rolled over. These fees will be distributed to the new affiliate instead.

## Recommendation
A possible fix would be to distinguish between ”repayment fees” and ”rollover fees”. With reference to:
```solidity
OriginationCalculator.sol#L133-L138
// Calculate amount to be sent to borrower for new loan minus rollover fees
uint256 borrowerFee = (newPrincipalAmount * feeData.borrowerRolloverFee) /
Constants.BASIS_POINTS_DENOMINATOR;
// Calculate amount to be collected from the lender for new loan plus rollover fees
uint256 interestFee = (interest * oldLoanData.feeSnapshot.lenderInterestFee) /
Constants.BASIS_POINTS_DENOMINATOR;
uint256 lenderFee = (newPrincipalAmount * feeData.lenderRolloverFee) /
Constants.BASIS_POINTS_DENOMINATOR;
```
interestFee and principalFee are repayment fees, while borrowerFee and lenderFee are rollover fees. In LoanCore.rollover(), instead of calculating fees using:
```solidity
feesEarned = _settledAmount - _amountToOldLender - _amountToLender - _amountToBorrower
```
The protocol could add two parameters named repaymentFee and rolloverFee, which are passed from OriginationController._rollover(). repaymentFee would then be split between the old loan's affiliate and the protocol, while rolloverFee is split between the new loan's affiliate and the protocol. Note that all rollover-related functions in OriginationController.sol will have to be refactored to accommodate this change as well.
