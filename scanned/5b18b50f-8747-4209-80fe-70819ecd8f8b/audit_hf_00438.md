# [M] The fee calculation in extendLoan leads to incorrect fee deductions

## Summary
Severity: Medium
Contest weight: 0.5916
Dataset id: 1860
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a borrower extends the loan duration, they are required to pay additional fees for the extended time. However, due to a calculation error, this fee may be incorrect, potentially causing the user to pay more than necessary.
// if user already paid the max fee, then we dont have to charge them again
```solidity
if (PorcentageOfFeePaid != maxFee) {
    // calculate difference from fee paid for the initialDuration vs the extra fee they should pay because of the extras days of extending the loan. MAXFEE shouldnt be higher than extra fee + PorcentageOfFeePaid
    uint feeOfMaxDeadline = ((offer.maxDeadline * feePerDay) / 86400);
    if (feeOfMaxDeadline > maxFee) {
        feeOfMaxDeadline = maxFee;
    } else if (feeOfMaxDeadline < feePerDay) {
        feeOfMaxDeadline = feePerDay;
    }
    misingBorrowFee = feeOfMaxDeadline - PorcentageOfFeePaid;
}
```
The calculation for feeOfMaxDeadline should be:
extendedLoanDuration * feePerDay,
where extendedLoanDuration represents the extended borrowing time. However, the function mistakenly uses the timestamp directly for calculations, leading to an incorrect fee computation.
Internal pre-conditions
External pre-conditions
Attack Path
The user might end up paying significantly higher fees than expected, leading to potential financial losses.
Borrowers will be charged inflated fees due to the incorrect calculation of the extended loan days. This results in unnecessary principal loss, making loan extensions disproportionately costly. Over time, this could discourage borrowers from using the loan extension feature, cause financial hardship, and lead to reputational damage for the platform as users perceive the fee structure as unfair or exploitative.

## Recommendation
```solidity
// if user already paid the max fee, then we dont have to charge them again
if (PorcentageOfFeePaid != maxFee) {
    // calculate difference from fee paid for the initialDuration vs the extra fee they should pay because of the extras days of extending the loan. MAXFEE shouldnt be higher than extra fee + PorcentageOfFeePaid
    uint feeOfMaxDeadline = (((offer.maxDeadline - loanData.startedAt) * feePerDay) / 86400);
    if (feeOfMaxDeadline > maxFee) {
        feeOfMaxDeadline = maxFee;
    } else if (feeOfMaxDeadline < feePerDay) {
        feeOfMaxDeadline = feePerDay;
    }
    misingBorrowFee = feeOfMaxDeadline - PorcentageOfFeePaid;
}
```
