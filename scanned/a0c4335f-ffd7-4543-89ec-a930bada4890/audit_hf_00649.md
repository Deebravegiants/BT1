# [C] C-02 | Some ProtocolVault Functions Do Not Validate Properly The PayloadType

## Summary
Severity: Critical
Contest weight: 0.1578
Dataset id: 2177
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the ProtocolVault contract, both the deposit and withdraw functions accept a PayloadType that is never validated against the function’s intended usage. As a result, a user could call the withdraw function but submit a payload indicating LP_DEPOSIT or SP_DEPOSIT. On the ledger side, this is interpreted as a deposit even though no tokens were transferred to the ProtocolVault, artificially increasing the user’s balance. This leads to unbacked shares on the ledger and allows users to perform “free” deposits.

## Recommendation
Add strict checks in each function to require that deposit only accepts deposit payloads (LP_DEPOSIT or SP_DEPOSIT) and withdraw only accepts withdrawal payloads (LP_WITHDRAW or SP_WITHDRAW). Any other PayloadType should always revert.
