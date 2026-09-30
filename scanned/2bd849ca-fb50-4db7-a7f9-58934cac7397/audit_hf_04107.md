# [C] VAULT-1 | Withdrawals Can Be Permanently Blocked

## Summary
Severity: Critical
Contest weight: 0.2153
Dataset id: 20564
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When withdrawing or redeeming from the Parifi Vault, a check is performed that the owner of the assets has passed the cooldown and if not, then it is considered that 0 assets can be withdrawn. Anyone can call functions withdraw or redeem for any depositor in the vault as long as they have the required allowance. Withdrawals and redemptions can be called with a 0 input amount. Execution will pass without the need for an allowance and the cooldown for the owner will be reset as if the owner has withdrawn. This is possible because there is no 0 amount validation in the execution path, neither in the allowance check nor in the withdrawal itself. An attacker can continuously call the withdraw or redeem functions for any other account with a 0 amount and delete their cooldown, effectively blocking that account from ever withdrawing their assets.

## Recommendation
In the withdraw and redeem functions from the ParifiVault contract, if the requested amount is 0, then return 0 as the first operation.
