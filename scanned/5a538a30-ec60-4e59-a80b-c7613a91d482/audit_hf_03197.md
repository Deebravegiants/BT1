# [M] executeBatchDeposit() will revert under cer-

## Summary
Severity: Medium
Contest weight: 0.0529
Dataset id: 17775
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DnGmxBatchingManager.executeBatchDeposit() will always revert if _convertAUsdcToAsset is called within DnGmxJuniorVault.deposit sub call because it will again call DnGmxBatchingManager.depositToken() and this will revert due to glp 15 mins cooldown. DnGmxBatchingManager.executeBatchDeposit() will revert under certain conditions

## Recommendation
No recommendation available
