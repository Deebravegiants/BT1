# [M] M-12 | Stepwise Jump After Update

## Summary
Severity: Medium
Contest weight: 0.1307
Dataset id: 22095
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A trader's pending funding and interest are calculated based on an accrued value which is updated
each time positions are updated based on the current rate and elapsed time.
The issue lies when admin updates funding or interest rate parameters without first realizing the
accumulated funding/interest with the old parameters.
Any rate increase/decrease would directly affect the funding/interest that a user would have to pay
(positively or negatively).
For example:
T0: User opens position, market caches interestRate = 2%
T5: Admin adjusts interest rate gradient, market interest rate should increase to 3% but
InterestRate.update not performed so new rate is not stored.
T10: User closes position
Interest owed calculated using 2% rate -- (calculateNextInterest uses the last cached rate)
Instead user should have been charged 2% from T0-T5, and 3% from T5-T10.

## Recommendation
Call recomputeFunding and updateInterestRate before updating funding or interest rate parameters
respectively.
