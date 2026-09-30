# [M] Borrow rate calculation can cause CToken.accrueInterest() to revert SumerMoney_report.md

## Summary
Severity: Medium
Contest weight: 0.1169
Dataset id: 15753
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
CToken hard-codes the maximum borrow rate BORROW_RATE_MAX_MANTISSA. Then we have accrueInterest() which reverts if the dynamically calculated rate borrowRateMantissa is greater or equal than the hard-coded one. Here is the check from accrueInterest():  
require(borrowRateMantissa <= BORROW_RATE_MAX_MANTISSA, 'borrow rate is absurdly high');  
The actual calculation is dynamic and takes no notice of the hard-coded cap, so it is very possible that this state will manifest, causing a major DoS due to most CToken functions calling accrueInterest() and accrueInterest() reverting.

## Recommendation
Change CToken.accrueInterest() to not revert in this case, but simply to set borrowRateMantissa = borrowRateMaxMantissa if the dynamically calculated value would be greater than the hard-coded max. This would:  
Allow execution to continue operating with the system-allowed maximum borrow rate, allowing all functionality that depends upon accrueInterest() to continue as normal.  
Allow borrowRateMantissa to be naturally set to the dynamically calculated rate as soon as that rate becomes less than the hard-coded max.
