# [M] Missing Invariant Check for Liquidation Threshold

## Summary
Severity: Medium
Contest weight: 0.2042
Dataset id: 9799
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The configuration logic found in both controller.lua and config.lua fails to enforce a critical invariant for lending safety: the LiquidationThreshold must be strictly greater than the CollateralFactor. This condition is necessary to ensure that borrowers are always at risk of liquidation before their collateral value drops below the borrowed amount, giving the protocol a safe buffer to cover debt positions during adverse price movements. Without this invariant enforced, an administrator may configure the pool with a CollateralFactor equal to or greater than the LiquidationThreshold, effectively allowing users to borrow more than the system can safely reclaim in a liquidation event. This misconfiguration directly undermines the protocol’s solvency assumptions and can lead to irrecoverable bad debt, especially during fast market downturns where prices can gap through the liquidation margin. Furthermore, the current inline documentation in config.lua is misleading. It comments that the "liquidation threshold (should be lower than the collateral factor)", which is incorrect and contradicts the intended safety model. The correct relationship is that the LiquidationThreshold should always be strictly higher than the CollateralFactor.

## Recommendation
The configuration validation logic should include an explicit check to enforce that LiquidationThreshold > CollateralFactor both in the main controller's token listing (controller.lua) and within the dynamic update routine (config.lua). If the condition is not met, the system should reject the update and return a descriptive error message to prevent misconfiguration. For example, in both configuration paths: assert( liquidationThreshold > collateralFactor, "Liquidation threshold must be greater than the collateral factor" ) This preserves the health of the lending pool and ensures that all borrow positions remain recoverable in a liquidation scenario. Lastly, update the documentation line in config.lua to reflect the correct logic: -- liquidation threshold (should be greater than the collateral factor)
