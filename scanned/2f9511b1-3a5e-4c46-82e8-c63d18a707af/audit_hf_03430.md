# [M] DPCU-3 | Capped PnL Leads To Incongruent Accounting

## Summary
Severity: Medium
Contest weight: 0.1168
Dataset id: 18731
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the event that a trader’s PnL is capped, the PnL they experience from price impact may not be accurately represented by the change in balance of the position impact pool, therefore perturbing the pool value. For example: A trader is positively impacted but their PnL is capped. The capping of their PnL essentially changes their executionPrice and negates the positive impact they received. However this positive impact is still removed from the position impact pool to offset the immediate gain in PnL the trader would have realized from the impact. Therefore the trader does not actually experience the PnL boost from the price impact amount, but that amount is still credited towards the pool value with the removal from the position impact pool.

## Recommendation
Consider computing what ought to be removed from the position impact pool after the trader’s PnL is capped.
