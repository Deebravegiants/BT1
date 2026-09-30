# [M] Swap fees are not applied to collateralDelta

## Summary
Severity: Medium
Contest weight: 0.0807
Dataset id: 19705
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Missing inclusion of swap fees can lead to inaccuracies in hedging when adjusting
long positions on GMX.
_collectSwapFees() is used to calculate the swap fee and deduct it from the token
output amount in the GMX Vault contract on line 545. GMXFuturesPoolHedger does
not include the swap fee when it calculates the collateralDelta for long positions
in _decreasePosition() and _increasePosition().
GMXFuturesPoolHedger does not accurately adjust the hedge position.

## Recommendation
Swap fees should be applied to collateralDelta before createIncreasePosition()
or createDecreasePosition() is called on GMX's PositionRouter.
