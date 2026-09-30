# [M] Inability to update node implementation in NativeVault

## Summary
Severity: Medium
Contest weight: 0.0817
Dataset id: 13975
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
NativeVault acts as a beacon for any node deployed through. The function NativeVault#changeNodeImplementation() that is used to update the beacon proxy implementation is restricted to the contract owner, which is the Core contract. However, the Core contract does not include any functionality to invoke changeNodeImplementation(). As a result, once a NativeVault is deployed, there's no way to update the nodeImpl for nodes that rely on NativeVault as a beacon.

## Recommendation
Depending on the intended behavior, make sure the NativeNode#changeNodeImplementation() can be called by the respective role within the project, e.g. MANAGER_ROLE.
