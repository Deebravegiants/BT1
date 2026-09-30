# [M] M-11 | Rounding Up Will DoS When Funds Are Withdrawn

## Summary
Severity: Medium
Contest weight: 0.1038
Dataset id: 2199
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When calculating distributeWithdrawAssets the value is rounded up. Because of this the amount of assets being distributed can be larger than the actual amount of funds. In some cases distributeWithdrawShares rounding down will offset this and there won't be excess funds distributed. But in situations where distributeWithdrawAssets does have a remainder causing the value to round up and distributeWithdrawShares does not have remainders resulting in no amount being rounded down. More assets will be distributed then intended. During times where all funds are withdrawn transferring an amount that is greater than what is available will lead to a failed transaction.

## Recommendation
Consider rounding down when calculating distributeWithdrawAssets.
