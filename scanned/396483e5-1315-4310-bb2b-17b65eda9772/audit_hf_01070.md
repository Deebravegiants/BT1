# [M] PAIR-2 | DoS Dividends

## Summary
Severity: Medium
Contest weight: 0.0637
Dataset id: 4066
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Due to the unbounded for loop in distributeDividends, there is a risk of a DoS attack. A malicious party can keep generating new addresses and minting minimal amounts of the BridgesPair token to make distributeDividends exceed the block gas limit, stopping all dividends.

## Recommendation
Process the users in smaller batches, set a cap on number of users who can receive dividends, or modify the dividend allocation logic entirely such that a for loop is not needed. For an alternative approach, see this “pointsPerShare” implementation: https://github.com/indexed-ﬁnance/dividends/tree/master/contracts
