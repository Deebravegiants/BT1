# [M] Corruptible Upgradability Pattern

## Summary
Severity: Medium
Contest weight: 0.1720
Dataset id: 13963
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Storage of vault contracts (e.g. DepositVault, RedemptionVault, ...) contracts might be corrupted during an upgrade.
Following is the inheritance of the DepositVault/RedemptionVault contracts.
defined. The contracts highlighted in Green mean that gap slots have been defined.
The vault contracts are meant to be upgradeable. However, it inherits contracts that are not upgrade-safe.
DepositVault/RedemptionVault/ManageableVault/WithMidasAccessControl.
Pausable/Greenlistable/Blacklistable/WithSanctionsList. Among these contracts, Pausable/Greenlistable/WithSanctionsList are contracts with defined variables (non pure-function), and they should have gaps as well.
Without gaps, adding new storage variables to any of these contracts can potentially overwrite the beginning of the storage layout of the child contract, causing critical misbehaviors in the system.
contracts and new variables are introduced, so this issue occurs again.
Also, CustomAggregatorV3CompatibleFeed does not have gaps but is inherited by MBasisCustomAggregatorFeed/MTBillCustomAggregatorFeed. If the feed wants to be upgradeable, CustomAggregatorV3CompatibleFeed should also have gaps.
Storage of vault contracts might be corrupted during upgrading.

## Recommendation
Add gaps for non pure-function contracts: Pausable/Greenlistable/WithSanctionsList/CustomAggregatorV3CompatibleFeed.
