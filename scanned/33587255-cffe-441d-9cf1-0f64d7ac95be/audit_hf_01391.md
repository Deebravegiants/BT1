# [M] M-11 Rewards rate can be set to 0

## Summary
Severity: Medium
Contest weight: 0.0709
Dataset id: 7125
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There is an issue with a depositrewardtoken function deﬁned at the line LiquidityGauge.vy#L680. It is possible to provide quite a big epoch compared to amount being deposited. It can cause the rate to be calculated as 0 here LiquidityGauge.vy#L695 and here LiquidityGauge.vy#L699. This issue has been assigned a MEDIUM severity level as it will lead to a small amount of reward tokens being stuck on a contract.

## Recommendation
We recommend calculating the rate value using precision to prevent divisions from leading to zeroes.
