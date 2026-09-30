# [M] Corruptible Upgradability Pattern

## Summary
Severity: Medium
Contest weight: 0.1442
Dataset id: 22799
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Storage of DepositVault/RedemptionVault/mTBILL contracts might be corrupted during an upgrade. Following are the inheritance of the DepositVault/RedemptionVault/mTBILL contracts. defined. The contracts highlighted in Green mean that gap slots have been defined. The DepositVault/RedemptionVault/mTBILL contracts are meant to be upgradeable. However, it inherits contracts that are not upgrade-safe. DepositVault/RedemptionVault/mTBILL/ERC20PausableUpgradeable. ManageableVault/Pausable/Greenlistable/Blacklistable/WithMidasAccessControl. Among these contracts, ManageableVault and WithMidasAccessControl are contracts with defined variables (non pure-function), and they should have gaps as well. Without gaps, adding new storage variables to any of these contracts can potentially overwrite the beginning of the storage layout of the child contract, causing critical misbehaviors in the system. Storage of DepositVault/RedemptionVault/mTBILL contracts might be corrupted during upgrading.

## Recommendation
Add gaps for non pure-function contracts: ManageableVault and WithMidasAccessControl.
