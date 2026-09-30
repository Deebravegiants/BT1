# [M] Borrowers can not extend loans

## Summary
Severity: Medium
Contest weight: 0.5945
Dataset id: 1858
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The logics to calculate the missing borrow fee is incorrect, which will cause the borrowers can not extend loans having maximum duration less than 24 hours because of arithmetic underflow
• In function DebitaV3Loan::extendLoan(), the borrower has to pay the extra fee if he has not paid maximum fee yet.
• The variable feeOfMaxDeadline is expected to be the fee to pay for lend offer's maximum duration, which is then adjusted to be within the range [feePerDay; maxFee]. This implies that the extra fee considers offer's min duration fee to be 1 day
• The fee paid for the initial duration is bounded to be within the range [minFEE; maxFee]
• The fee configurations are set initially as. The fee implies that min fee for the loan initial duration is 0.2% , = 5 days of fee
uint public feePerDay = 4; // fee per day (0.04%)
uint public maxFEE = 80; // max fee 0.8%
uint public minFEE = 20; // min fee 0.2%
• The extra fee to be paid is calculated as misingBorrowFee = feeOfMaxDeadline - PorcentageOfFeePaid, which will revert due to arithmetic underflow in case the loan's initial duration is less than 24 hours and the unpaid offers' maximum duration is also less than 24 hours. In this situation, the values will satisfy PorcentageOfFeePaid = minFEE = 0.2%, feeOfMaxDeadline = feePerDay = 0.04%, which will cause misingBorrowFee = feeOfMaxDeadline - PorcentageOfFeePaid to revert because of arithmetic underflow
```solidity
uint feePerDay = Aggregator(AggregatorContract).feePerDay();
uint minFEE = Aggregator(AggregatorContract).minFEE();
uint maxFee = Aggregator(AggregatorContract).maxFEE();

uint PorcentageOfFeePaid = ((m_loan.initialDuration * feePerDay) / 86400);
// adjust fees
if (PorcentageOfFeePaid > maxFee) {
    PorcentageOfFeePaid = maxFee;
} else if (PorcentageOfFeePaid < minFEE) {
    PorcentageOfFeePaid = minFEE;
}
// calculate interest to pay to Debita and the subtract to the lenders
for (uint i; i < m_loan._acceptedOffers.length; i++) {
    infoOfOffers memory offer = m_loan._acceptedOffers[i];
    // if paid, skip
    // if not paid, calculate interest to pay
    if (!offer.paid) {
        uint alreadyUsedTime = block.timestamp - m_loan.startedAt;
        uint extendedTime = offer.maxDeadline - alreadyUsedTime - block.timestamp;
        uint interestOfUsedTime = calculateInterestToPay(i);
        uint interestToPayToDebita = (interestOfUsedTime * feeLender) / uint misingBorrowFee;
        // if user already paid the max fee, then we dont have to charge them again
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
    }
}
```
Internal pre-conditions
External pre-conditions
Attack Path
1. A borrow offer is created with duration = 5 hours
2. A lend offer is created with min duration = 3 hours, max duration = 12 hours
3. 2 offers matched
4. After 4 hours, the borrower decides to extend loan by calling extendLoan() and transaction gets reverted
• Borrowers can not extend loan for the loans having durations less than 24 hours (both initial duration and offers' max duration)

## Recommendation
Consider updating like below
```solidity
} else if (feeOfMaxDeadline < feePerDay) {
    feeOfMaxDeadline = feePerDay;
} else if (feeOfMaxDeadline < minFEE) {
    feeOfMaxDeadline = minFEE;
}
```
