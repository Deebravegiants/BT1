# [M] M-01 | Fill Price Causes Funding And Utilization Discrepancy

## Summary
Severity: Medium
Contest weight: 0.1362
Dataset id: 21101
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the Position.validateTrade function the params.fillPrice is used to compute the marginValues,
which include the funding and utilization fees based upon that price. However the funding and
utilization fees should not be based upon the fillPrice, as this price includes a premium/discount
according to how the trade affects the market skew.
This will lead to shorts paying less fees when they push the skew increasingly short, or longs paying
more fees when they push the skew increasingly long.
Additionally, when the currentFundingAccruedComputed and currentUtilizationAccruedComputed is
accounted for the market with the recomputeUtilization and recomputeFunding functions these
values are based upon the pythPrice. As a result traders will experience a discrepancy in the amount
of funding and utilization fees paid to the market’s recorded funding and utilization accrued values.

## Recommendation
Consider using the params.oraclePrice specifically for the funding and utilization fee calculations
when computing the marginValues in the Position.validateTrade function.
