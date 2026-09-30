# [M] ORDM-10 | Liquidations Revert With 0 netPnl

## Summary
Severity: Medium
Contest weight: 0.1120
Dataset id: 20558
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the _liquidatePosition function, the netPnl is capped to the userPosition.positionCollateral amount before the liquidationThreshold validation. Therefore if the user’s position has 0 collateral, the netPnl will be assigned to 0 and subsequently fail the validation on line 574 as the liquidationThreshold is also 0. There is no straightforward path to getting a position with 0 collateral, however the liquidation logic should be refactored as certainly any position with 0 collateral must be liquidated. Additionally, in the case that the netPnl is capped to 0, the safeTransfer and fee distribution on lines 593 and 594 should not occur as certain tokens may revert on 0 transfers.

## Recommendation
Cap the netPnl to the userPosition.positionCollateral after the liquidationThreshold is validated. Additionally, do not execute the fee distribution logic if the netPnl is 0.
