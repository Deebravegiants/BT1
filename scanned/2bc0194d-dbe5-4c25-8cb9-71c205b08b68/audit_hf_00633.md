# [M] M-06 | Frontrun Restructure Bad Debt

## Summary
Severity: Medium
Contest weight: 0.0872
Dataset id: 2134
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When restructureBadDebt is called, the exchangeRate will immediately decrease due to the reduction in _totalBalance without a proportional reduction in pool token supply. A user can frontrun the restructuring to redeem before the exchange rate drop to avoid the penalty. The LP exploiting this receives yield without risk while increasing the risk of all the other LP as the bad debt is socialized among all other LPs. Furthermore, the LP taking advantage of the stepwise jump in the exchange rate can then mint the same amount of PoolTokens for a fraction of the price.

## Recommendation
Consider a 2 step deposit/redeem process.
