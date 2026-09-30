# [M] Corruptible Upgradability Pattern

## Summary
Severity: Medium
Contest weight: 0.1164
Dataset id: 7729
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Registry.sol contract is a UUPSUpgradeable contract that inherits from the RegistryHelper.sol contract. When creating upgradable contracts that inherit from other contracts, it is important that there are storage gaps in case storage variables are added to inherited contracts. If an inherited contract is a stateless contract (i.e. it doesn't have any storage) then it is acceptable to omit a storage gap since these function similarly to libraries and aren't intended to add any storage. The issue is that Registry.sol inherits from a contract that contains storage that doesn't contain any gaps such as RegistryHelper.sol. These contracts can pose a significant risk when updating a contract because they can shift the storage slots of all inherited contracts.

## Recommendation
Consider adding storage gaps to the RegistryHelper.sol contract.
