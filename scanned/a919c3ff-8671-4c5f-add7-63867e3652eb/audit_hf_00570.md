# [H] H-01 | Claimable Collateral Cannot Be Claimed

## Summary
Severity: High
Contest weight: 0.0882
Dataset id: 2032
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The ExchangeRouter.claimCollateral is not implemented in the GmxV2PositionManager contract. Quoted from the GMX docs: If negative price impact is capped, the additional amount would be kept in the claimable collateral pool, this needs to be manually claimed using the ExchangeRouter.claimCollateral function.

## Recommendation
Implement the claimCollateral function.
