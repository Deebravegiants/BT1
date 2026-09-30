# [H] BOU-2 | Stop-loss Won’t Execute On Price Gap

## Summary
Severity: High
Contest weight: 0.1433
Dataset id: 18515
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The prices for a stop-loss are required to straddle the trigger price in setExactOrderPrice. In the case
of a price gap where both the primary and secondary prices fall below/above the trigger price, the
stop-loss will fail to execute. This will prevent a position’s profit from being secured or loss to be
mitigated.
For example, if the trigger price is $100 for a long SL but price gaps to $99 (primary) -> $98
(secondary) the SL will not be triggered and the user will still have exposure in the market.

## Recommendation
Do not revert if both primary and secondary prices fall below/above the trigger price.
