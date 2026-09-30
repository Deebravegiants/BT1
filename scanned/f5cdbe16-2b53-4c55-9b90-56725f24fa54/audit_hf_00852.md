# [M] M-12 | Legacy Market Unable To Claim SNX Rewards

## Summary
Severity: Medium
Contest weight: 0.0848
Dataset id: 2589
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Unclaimed SNX rewards in V2X FeePool are rolled over each week and can be claimed by any debt shareholder. As a large debt shareholder, Legacy Market can claim an estimated 500 SNX tokens each week, until all rolled over rewards are exhausted (around 2000 tokens remain). However, Legacy Market currently lacks the ability (no implemented functions) to claim and vest these tokens from V2X FeePool. In the worst case, if all debt shares are migrated then these tokens will permanently remain unclaimed in the FeePool.

## Recommendation
Consider adding functions to allow Legacy Market to claim and vest of these rewards.
