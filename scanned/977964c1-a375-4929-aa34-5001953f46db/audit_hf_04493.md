# [M] M-02 | Incorrect BPOOL Locked State

## Summary
Severity: Medium
Contest weight: 0.0882
Dataset id: 22056
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
ERC20 features are moved from BPOOL to separate BToken contract with the current update. However, the locked status still remains in the BPOOL contract, in addition to the BToken contract, creating an asymmetry. The setTransferLock function correctly updates the locked status of the BToken contract, but there is no mechanism to update the locked status in BPOOL. Since BPOOL.locked is set to true in the constructor, it will always appear locked. This will lead to discrepancies for integrators who read BPOOL.locked instead of BPOOL.bToken.locked.

## Recommendation
Remove the locked from the BPOOL and use it only from the BToken.
