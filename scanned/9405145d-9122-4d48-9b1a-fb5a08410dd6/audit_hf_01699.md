# [M] Interest acquired on debt compounds when it shouldn't

## Summary
Severity: Medium
Contest weight: 0.1399
Dataset id: 9310
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Users can create vault in which they deposit collateral in exchange for minting the protocol's stable coin debt token - KEI. When users have debt their debt acquires interest over time. When interest is acquired it is added to the totalDebt amount of the user's vault. This however is a problem since the next time a user acquires interest, interest would be added on top of the interest that was last acquired, effectively compounding. Example a user has 10_000 in debt with 2 % interest per year. If his interest is updated only one at the end of the 365 day he will not have 10_000 + 2 % = 10_200 debt. However if the his interest is updated once on the 6th month and once on the 12th that would equal to: 10_000 + 1 % = 10_100 + 1 % = 10_101 debt. Having in mind that the lower the min CR a user sets the higher interest he gets and that anyone could call updateVaultInterest at anytime, a user's debt could grow a lot faster than expected.

## Recommendation
Use a separate mapping to store the acquired interest and gather interest only on the base debt amount.
