# [H] H-02 | Collateral Returned Despite Bad Debt

## Summary
Severity: High
Contest weight: 0.1795
Dataset id: 1980
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a trader is closing out a position, if the loss exceeds collateral deposited then this case is entered. As bad debt has been incurred, the collateral should be reduced to zero but currently depositedCollateralAmount remains unchanged. The extraCollateralRequired would cover the losses, but however it is only taken into account if the trader is re-opening a new position. So, If the trader was closing the position (i.e. size = 0), then all deposited collateral is returned implying losses are borne by the protocol/other LPs and traders.

## Recommendation
Change the logic to: if (collateralLoss > params.oldPosition.depositedCollateralAmount) output.position.depositedCollateralAmount = 0; extraCollateralRequired = collateralLoss - params.oldPosition.depositedCollateralAmount;
