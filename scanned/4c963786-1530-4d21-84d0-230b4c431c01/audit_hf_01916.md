# [M] BasicVault::_deposit() should always resolve with idle balance as the redeem queue may be disabled with requests pending

## Summary
Severity: Medium
Contest weight: 0.0490
Dataset id: 10525
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
BasicVault::_deposit() only calls BasicVault::_resolveWithIdleBalance() if the redeem queue is enabled; however, requests must be claimed if they were created before the redeem queue was disabled, so the idle balance must be reserved even when the redeem queue is disabled.

## Recommendation
Always resolve with idle balance in the BasicVault::_deposit() function.
