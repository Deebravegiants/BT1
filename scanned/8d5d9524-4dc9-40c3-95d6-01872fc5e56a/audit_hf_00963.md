# [M] Reusable signatures can be repeatedly rolled over with rolloverLoan() to incur extra fees

## Summary
Severity: Medium
Contest weight: 0.4546
Dataset id: 3024
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
If a user with a reusable signature enters a loan, the other party can just repeatedly call rolloverLoan() with the same signature to consume all their signatures. Assuming that all fees are at 0%, this will just incur gas costs for the attacker. The more serious impact is if:
• The victim granted infinite approval of payableCurrency to the OriginationController contract.
• Fees are not at 0%.
By repeatedly calling rolloverLoan(), an attacker can cause the other party to keep incurring fees. Fees for rollovers are calculated in _calculateRolloverAmounts():
```solidity
// Calculate amount to be sent to borrower for new loan minus rollover fees
uint256 borrowerFee = (newPrincipalAmount * feeData.borrowerRolloverFee) /
Constants.BASIS_POINTS_DENOMINATOR;
// Calculate amount to be collected from the lender for new loan plus rollover fees
uint256 interestFee = (interest * oldLoanData.feeSnapshot.lenderInterestFee) /
Constants.BASIS_POINTS_DENOMINATOR;
uint256 lenderFee = (newPrincipalAmount * feeData.lenderRolloverFee) /
Constants.BASIS_POINTS_DENOMINATOR;
```
Assuming that a principal fee is implemented for rolloverLoan(), for each rollover:
• Borrower will incur rollover fees.
• Lender will incur rollover and principal fees. There are no interest fees if the attacker calls rolloverLoan() repeatedly, since no time has passed since loan creation.
An example where repeatedly calling rolloverLoan() to grief the opposite party is likely:
• Rollover fees are at 0%, but principal fees are non-zero.
• Lender signs a reusable signature and grants infinite approval to the OriginationController contract.
• After the lender enters a loan, the borrower repeatedly calls rolloverLoan():
– Lender will pay principal fees for each rollover.
– However, the borrower doesn't pay any fees.

## Recommendation
Ensure that rollover fees are always greater than principal fees. More specifically, FL_03, which is the borrowerRolloverFee, should always be more than FL_07, the lenderPrincipalFee. This ensures that it is never economically viable to perform the attack described above.
Arcade: Code refactoring in PR-108 addresses the issue.
