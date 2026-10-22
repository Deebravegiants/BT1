# [M] M-42 | Not Updating Pairs Will Break LAV

## Summary
Severity: Medium
Contest weight: 0.0795
Dataset id: 22214
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a deposit or withdraw happens in the LendingAssetVault all pairs should be updated because the totalAssets are increased unilaterally which affects the pairs. There is a function which allows setting _updateInterestOnVaults to be set to false. If so, any updates to all pair at once will be skipped. This means users can manipulate pairs' utilization rates by depositing/withdrawing.

## Recommendation
_updateInterestOnVaults is meant to be set to false if updating all vaults start causing OOG errors. Given the problem it creates and the facts that there is a limit to the maximum pairs that can be connected to a vault and that pairs can also be removed, the removal of _updateInterestOnVault is best.
