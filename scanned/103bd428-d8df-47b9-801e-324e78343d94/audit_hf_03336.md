# [M] DPU-2 | Drain Keeper’s Gas Through Liquidations

## Summary
Severity: Medium
Contest weight: 0.1043
Dataset id: 18187
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A trader is allowed to decrease their position such that the collateral is below the minimum collateral because shouldValidateMinCollateralUsd is false. However, shouldValidateMinCollateralUsd is set to true for liquidation orders. Therefore, a trader’s decrease order can go through and their position can be liquidated right after by a liquidation keeper. An attacker may leverage this to drain the keeper of its gas by creating trivial positions and decreasing them to invalidate the minimum collateral so that they are subsequently liquidated.

## Proof of Concept
https://github.com/GuardianAudits/GMX_3/blob/main/test/Guardian/PoCs/DPU_2.ts

## Recommendation
Always validate the minimum collateral amount when decreasing or increasing a position.
