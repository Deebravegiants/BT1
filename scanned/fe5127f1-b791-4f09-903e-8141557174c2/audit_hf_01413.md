# [M] Potential DoS in _distributeExcessIdleSafe

## Summary
Severity: Medium
Contest weight: 0.1743
Dataset id: 7278
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• HyperdriveLP.sol#L527-L532: Use the safe version of LPMath.calculateUpdateLiquiditySafe here instead:
// Remove the withdrawal pool proceeds from the reserves.
success = _updateLiquiditySafe(-shareProceeds.toInt256()); // <--- needs to be defined
if (!success) {
return false;
}
// note that we swapped the update of these storage parameters incase
// `_updateLiquiditySafe` fails
// Update the withdrawal pool's state.
_withdrawPool.readyToWithdraw += withdrawalSharesRedeemed.toUint128();
_withdrawPool.proceeds += shareProceeds.toUint128();
return true;
• LPMath.sol#L759-L761: Use calculatePresentValueSafe since one ends up in this scope only through _distributeExcessIdleSafe which is supposed to be a safe function (no reverts when underflowing):
• YieldSpaceMath.sol#L508: Use calculateEffectiveShareReservesSafe and bubble up failure, otherwise in some cases _distributeExcessIdleSafe would not be safe:

## Recommendation
• HyperdriveLP.sol#L527-L532: Use the safe version of LPMath.calculateUpdateLiquiditySafe here instead:
// Remove the withdrawal pool proceeds from the reserves.
success = _updateLiquiditySafe(-shareProceeds.toInt256()); // <--- needs to be defined
if (!success) {
return false;
}
// note that we swapped the update of these storage parameters incase
// `_updateLiquiditySafe` fails
// Update the withdrawal pool's state.
_withdrawPool.readyToWithdraw += withdrawalSharesRedeemed.toUint128();
_withdrawPool.proceeds += shareProceeds.toUint128();
return true;
• LPMath.sol#L759-L761: Use calculatePresentValueSafe since one ends up in this scope only through _distributeExcessIdleSafe which is supposed to be a safe function (no reverts when underflowing):
• YieldSpaceMath.sol#L508: Use calculateEffectiveShareReservesSafe and bubble up failure, otherwise in some cases _distributeExcessIdleSafe would not be safe:
