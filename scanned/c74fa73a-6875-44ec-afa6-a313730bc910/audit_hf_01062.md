# [M] GG-1 | DoS Dividends

## Summary
Severity: Medium
Contest weight: 0.0731
Dataset id: 4049
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to the unbounded for loop in distributeDividends, there is a risk of a DoS attack. Anytime a new address deposits to pool 0, they are added to the usersBridges list. A malicious party can keep generating new addresses and deposit miniscule amounts of LP to make distributeDividends exceed the block gas limit, stopping all dividends.

## Recommendation
Process the users in smaller batches, set a cap on number of users who can receive dividends, or modify the dividend allocation logic entirely such that a for loop is not needed.
For an alternative approach, see this “pointsPerShare” implementation:
https://github.com/indexed-ﬁnance/dividends/tree/master/contracts
