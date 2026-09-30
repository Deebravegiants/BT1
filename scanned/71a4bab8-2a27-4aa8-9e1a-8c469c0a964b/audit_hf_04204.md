# [H] H-02 | Liquidation Computes Utilization Before Updating Market Size

## Summary
Severity: High
Contest weight: 0.2109
Dataset id: 21097
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During liquidatePosition, updateMarketPreLiquidation is called to perform pre-steps and validation,
including the recomputation of utilization. market.recomputeUtilization is incorrectly called before
market.size is reduced by the liquidation size. The new utilization rate should be calculated with the
new market size, similar to settleOrder in OrderModule.sol.
By calling recomputeUtilization before updating size, the liquidation leaves utilization rate unchanged
when it should have reduced it, affecting all remaining traders.
Assume the utilization rate was very high, and a large position was just liquidated. This should in
effect bring down utilization rate and improve the margins of all other traders. However, due to this
error, the margins of all other traders remain unchanged, which could then lead to unfair liquidations.

## Recommendation
Call recomputeUtilization after market size and skew are updated in the updateMarketPreLiquidation
function.
