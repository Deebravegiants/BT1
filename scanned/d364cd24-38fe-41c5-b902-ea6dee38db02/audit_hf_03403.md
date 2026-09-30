# [H] TIME-1 | Wrong Key For Signer Removal

## Summary
Severity: High
Contest weight: 0.1170
Dataset id: 18511
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a remove oracle signer is signaled, the action key used is:
bytes32 actionKey = _removeOracleSignerActionKey(account);
However, removeOracleSignerAfterSignal uses an incorrect action key to validate the signal.
Specifically, it uses _addOracleSignerActionKey instead of _removeOracleSignerActionKey.
Therefore a signer cannot be removed using the removeOracleSignerAfterSignal function.

## Recommendation
Use the _removeOracleSignerActionKey in the removeOracleSignerAfterSignal function.
