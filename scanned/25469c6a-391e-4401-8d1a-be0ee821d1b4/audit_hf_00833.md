# [M] M-04 | Missing Check In Migrate Flow

## Summary
Severity: Medium
Contest weight: 0.0762
Dataset id: 2569
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• Liquidating a vault can be very profitable for the liquidator. • The _migrate function does not check if the vault is liquidatable. This allows to bring the vault into an unhealthy state on purpose, or to increase the profit for the liquidator further: • The migration of an unhealthy V2 position can bring the SNX vault into an unhealthy state. • It is possible to migrate more assets into a vault that is already liquidatable to increase the profit further.

## Recommendation
Revert at the end of the migration flow if the vault is liquidatable.
