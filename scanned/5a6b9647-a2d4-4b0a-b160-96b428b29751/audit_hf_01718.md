# [M] M-7 Anonymous call

## Summary
Severity: Medium
Contest weight: 0.0497
Dataset id: 9360
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
• EntryPoint.sol#L66  
Any anonymous user on the Kinto network can call an empty handleOps or handleAggregatedOps. This is not a threat, but it does create an exploitable contract (e.g. in the first 1000 blocks after the network starts) that can be called anonymously from any account.

## Recommendation
We recommend considering this when deploying contracts.
