# [H] H-4 An incorrect rate update

## Summary
Severity: High
Contest weight: 0.0870
Dataset id: 7070
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
rate is fetched before epoch update in the CRV contract LiquidityGauge.vy#L237-L238 which can lead to an incorrect rate being saved to the storage. This finding is classified as HIGH severity because an incorrect rate update will lead to incorrect CRV distribution to users.

## Recommendation
We recommend fetching rate after the epoch update in the CRV contract.
