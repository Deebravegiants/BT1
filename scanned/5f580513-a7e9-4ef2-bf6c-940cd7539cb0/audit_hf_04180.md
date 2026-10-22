# [H] H-02 | Interest Calculation Set To Min Interest

## Summary
Severity: High
Contest weight: 0.5743
Dataset id: 20861
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When initializing a new loan, the user will pass both _duration and _amount parameters. If both amount and duration are variable, the interest should be calculated based on scaling both duration and amount. The issue arises due to the inherent rounding down behavior in Solidity. When calculating the average amount and duration, they are rounded down to 0. After multiplying with (loanConﬁg.maxInterest - loanConﬁg.minInterest), the result is 0. Consequently, the interest is always set as loanConﬁg.minInterest, resulting in the lender missing out on potential additional interest due to rounding down. • Example: If minAmount = 100, maxAmount = 200, and _amount=150 • (_amount - loanConﬁg.minAmount) / (loanConﬁg.maxAmount - loanConﬁg.minAmount) • (150 - 100) / (200 - 100) = 50 / 100 = 0 • The same happens with duration.

## Recommendation
Calculate in the following manner to prevent rounding down:
```solidity
interest =
loanConfig.minInterest +
uint32(
(// Take average of amount and duration factors
(((_amount - loanConfig.minAmount) * (loanConfig.maxInterest - loanConfig.minInterest)) /
(loanConfig.maxAmount - loanConfig.minAmount)) +
(((_duration - loanConfig.minDuration) * (loanConfig.maxInterest - loanConfig.minInterest)) /
(loanConfig.maxDuration - loanConfig.minDuration))
) / 2
);
```
