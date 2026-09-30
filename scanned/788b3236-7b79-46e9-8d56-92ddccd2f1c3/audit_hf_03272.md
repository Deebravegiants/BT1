# [M] Deregistering inactive knot via calling deRegisterKnots directly

## Summary
Severity: Medium
Contest weight: 0.1452
Dataset id: 17966
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Deregistering inactive knot via calling deRegisterKnots directly by the Syndicate owner always reverts.

**Actual Behaviour & Impact**  
The liquid staking manager (Syndicate owner) calls `deRegisterKnots` function to deregister knots. However, if any of those knots is inactive, the transaction will revert. This means in order to deregister an inactive knot, one should call `updateCollateralizedSlotOwnersAccruedETH` function since it calls internal `_deRegisterKnots`.

**Expected Behaviour**  
Deregistering knots by Syndicate owner should succeed especially if the knot is inactive.

**Cause**  
There is a circular dependency between deRegisterKnots and `_updateCollateralizedSlotOwnersLiabilitySnapshot` functions which leads to this behaviour.

`deRegisterKnots` always calls internally `_updateCollateralizedSlotOwnersLiabilitySnapshot`, and `_updateCollateralizedSlotOwnersLiabilitySnapshot` calls `_deRegisterKnot` in case the knot is inactive. So when the knot is deregistered the first time, the second time it reverts.

## Recommendation
No recommendation
