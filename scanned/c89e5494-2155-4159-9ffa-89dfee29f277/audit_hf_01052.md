# [M] M-01 | Front-Running Risk In startVault Function

## Summary
Severity: Medium
Contest weight: 0.1515
Dataset id: 4026
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The startVault function in the BracketVault contract is susceptible to front-running. This function is designed to move the vault from its initial state (Epoch 0) to an active state (Epoch 1), transferring all deposited assets to the manager to kick off operations.
During Epoch 0, users can deposit tokens and withdraw them instantly via the _withdrawEpoch0 function, which does not impose delays or penalties.
An attacker can exploit this setup by depositing a large quantity of tokens right before the startVault transaction, ensuring their deposit is recorded, and then withdrawing those tokens using _withdrawEpoch0 front-running the startVault call.
As a result, when startVault executes, it transfers only the remaining deposits, excluding the attacker’s withdrawn amount, to the manager. This reduces the capital available to the manager, disrupting the vault’s intended starting liquidity.

## Recommendation
Consider updating the startVault function to include an additional parameter, minTotalDeposits, which specifies the minimum amount of deposits required to proceed with starting the vault. The function should check the current total deposits against this threshold and revert if the amount is insufficient.
This ensures that the vault only transitions to Epoch 1 when a predefined level of funding is secured, limiting the impact of last second withdrawals.
