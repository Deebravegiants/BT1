# [M] GLOBAL-2 | Inherent AMM Risk

## Summary
Severity: Medium
Contest weight: 0.0680
Dataset id: 106
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The AMM currently only hedges to be delta neutral. However, it is still vulnerable to volatility risk as the AMM is not vega neutral. Inherently as part of the hedging process, the AMM will have to buy at higher prices and sell at lower prices to maintain delta neutral status. Alongside the volatility in the market, there is a risk that the AMM may not have positive expected value.

## Recommendation
Carefully monitor AMM status and increase fees when necessary to protect against losses due to vega non-neutrality.
