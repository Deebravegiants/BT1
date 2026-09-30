# [M] Unnecessary precision loss in_recipientBalance()

## Summary
Severity: Medium
Contest weight: 0.5382
Dataset id: 17830
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Using ratePerSecond() to calculate the _recipientBalance() incurs an unnecessary precision loss. The current formula in _recipientBalance() to calculate the vested amount (balance) incurs an unnecessary precision loss, as it includes div before mul:
```solidity
balance = elapsedTime_ * (RATE_DECIMALS_MULTIPLIER * tokenAmount_ / duration) / RATE_DECIMALS_MULTIPLIER
```
This can be avoided and the improved formula can also save some gas. Precision loss in _recipientBalance().

## Recommendation
Consider changing to:
```solidity
balance = elapsedTime_ * tokenAmount_ / duration
```
