# [M] Strategy withdraw may fail if weights of strategies differ from the real values and might lead to frozen ReservePool

## Summary
Severity: Medium
Contest weight: 0.0735
Dataset id: 8547
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When depositing or withdrawing in the ReservePool, it deposits/withdraws individually from the strategies based on the weights. In the case of withdrawals, the transaction might revert. Suppose default strategy with 50% weight and AaveV3 strategy with 50% weight. AaveV3 yield reduces, such that its amount is no longer 50%, but 49%. In the ReservePool, withdraw(), the transaction will revert because it tries to withdraw 50% from the AaveV3 strategy, which will revert.

## Recommendation
Call the getBalance() (
