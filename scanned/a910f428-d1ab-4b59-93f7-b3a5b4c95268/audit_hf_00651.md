# [C] C-04 | State Variables Are Updated After A Failed Check

## Summary
Severity: Critical
Contest weight: 0.1343
Dataset id: 2180
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ProtocolVaultLedger contract, the _checkWithdraw function merely emits an event and returns early if a user attempts to withdraw more shares than they hold, instead of reverting the entire transaction. Because control flow proceeds after this early return, the contract continues to update its state variables (e.g., incrementing frozenShares or proceeding with other post-withdraw steps) even when the user’s withdrawal request is invalid.

## Recommendation
In case that the _checkWithdraw function require check was not passed, ensure that the frozenShares state variable is not updated.
