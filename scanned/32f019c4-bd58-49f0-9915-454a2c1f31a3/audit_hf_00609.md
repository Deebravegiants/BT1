# [M] M-08 | Position Fee Not Factored Into Margin

## Summary
Severity: Medium
Contest weight: 0.0987
Dataset id: 2108
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During liquidation, when _isMaintenanceMarginSafe is called, pending borrow fees are included in the required Maintenance Margin (MM). However, the position fee is not factored into the MM calculation. Since this position fee depends on the position value, it can sometimes be substantial. In such cases, _isMaintenanceMarginSafe might return true, even when the collateral is insufficient to cover the position fee. Despite this, the liquidation proceeds due to shouldCollateralSufficient = false in _dispatchPositionFee, leading to unpaid fees. This results in lost fee revenue for LPs and veMUX holders.

## Recommendation
Update _isMaintenanceMarginSafe to account for the liquidation position fee as part of the collateral sufficiency check.
