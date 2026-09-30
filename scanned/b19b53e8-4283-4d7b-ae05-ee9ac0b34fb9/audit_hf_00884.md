# [M] Missing slippage control for certain router

## Summary
Severity: Medium
Contest weight: 0.1191
Dataset id: 2640
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Router actions such as CollVaultRouter::redeemCollateralVault() only check slippage when the CollVault asset is unwrapped. However, the amount of collateral to redeem depends on the price of the collateral, which means the amount of collateral redeemed may vary a lot and the user has no control over it. Router actions such as CollVaultRouter::redeemCollateralVault() do not validate the amount of collateral redeemed if it is not unwrapped. Internal Pre-conditions None. External Pre-conditions None. Attack Path 1. User calls CollVaultRouter::redeemCollateralVault() without unwrapping and loses significant collateral due to a price drop in the meantime. Loss of funds.

## Proof of Concept
CollVaultRouter::redeemCollateralVault() DenManager::_removeCollateralFromDen()

## Recommendation
Always place slippage control whenever there is a price.
