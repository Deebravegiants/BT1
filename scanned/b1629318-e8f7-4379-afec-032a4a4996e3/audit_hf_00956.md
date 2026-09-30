# [H] Underflow in InterestCalculator.sol allows Borrower to default a loan and deny Lender from claiming collateral

## Summary
Severity: High
Contest weight: 0.6429
Dataset id: 3013
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a loan is past loanStartTime + loanDuration, a Lender can now call RepaymentController.claim() to claim the loan's collateral, but only after loanStartTime + loanDuration + Constants.GRACE_PERIOD + 1 has passed.

The Borrower who has defaulted on the loan can now call RepaymentController.repay() and repay a minimum (the accrued interest), and loans[loanId].lastAccrualTimestamp = uint64(block.timestamp) will get updated.

This turns out to be a vulnerability because, after the Grace Period has passed, the Lender will try to call RepaymentController.claim(). However, the call to getProratedInterestAmount() will try to fetch the interest on which a default fee is owed, but the code inside InterestCalculator.getProratedInterestAmount() will revert because timeSinceStart > loanDuration and lastAccrualTimestamp > endTimestamp.

Therefore InterestCalculator.sol#51 underflows, causing a revert, which means the Lender cannot claim the collateral indefinitely.

```solidity
function getProratedInterestAmount(
    uint256 balance,
    uint256 interestRate,
    uint256 loanDuration,
    uint256 loanStartTime,
    uint256 lastAccrualTimestamp,
    uint256 currentTimestamp
) public pure returns (uint256 interestAmountDue) {
    // time since loan start
    uint256 timeSinceStart = currentTimestamp - loanStartTime;
    // time since last payment
    uint256 timeSinceLastPayment;
    if (timeSinceStart > loanDuration) {
        // if time elapsed is greater than loan duration, set it to loan duration
        uint256 endTimestamp = loanStartTime + loanDuration;
        timeSinceLastPayment = endTimestamp - lastAccrualTimestamp;
    } else {
        timeSinceLastPayment = currentTimestamp - lastAccrualTimestamp;
    }
    interestAmountDue = balance * timeSinceLastPayment * interestRate / (Constants.BASIS_POINTS_DENOMINATOR * Constants.SECONDS_IN_YEAR);
}
```

## Recommendation
In getProratedInterestAmount(), when lastAccrualTimestamp is greater than the loan's endTimestamp, return the amount of interest owed as 0:

```diff
@@ -47,10 +47,14 @@ abstract contract InterestCalculator {
    uint256 timeSinceLastPayment;
    if (timeSinceStart > loanDuration) {
        // if time elapsed is greater than loan duration, set it to loan duration
        uint256 endTimestamp = loanStartTime + loanDuration;
+
        if(lastAccrualTimestamp >= endTimestamp) {
+
            return 0;
+
        }
+
        timeSinceLastPayment = endTimestamp - lastAccrualTimestamp;
    } else {
        timeSinceLastPayment = currentTimestamp - lastAccrualTimestamp;
    }
```
