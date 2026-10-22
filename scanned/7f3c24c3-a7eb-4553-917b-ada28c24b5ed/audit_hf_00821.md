# [M] M-23 | Reallocate Will Redeem Assets Instead of Shares

## Summary
Severity: Medium
Contest weight: 0.0695
Dataset id: 2557
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Owner can reallocate funds by redeeming from certain pools and depositing into different pools. The issue arises when executing POOL.redeem as it uses assets instead of shares. Not only owner will redeem more assets than expected, but assets might not be fully deposited during the second loop as total assets redeemed will be greater that deposits total assets.

## Recommendation
The withdraws array should contain shares instead of assets amount. Alternatively, calculate the shares that need to be redeemed with the asset amount passed and use that value in POOL.redeem().
