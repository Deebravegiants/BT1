# [M] Slippage protection for wakeSleepers()

## Summary
Severity: Medium
Contest weight: 0.0690
Dataset id: 8774
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
All Jars are equal in terms of value and can be used to receive tokens locked in Sleepers. Users cannot choose exact Sleepers, the next available Sleeper is always used. It is considered a game mechanic. The problem is that User Alice can sign a transaction expecting to receive a Sleeper 2, but during the transaction execution, someone frontrun the user and now Alice spends a Jar to receive Sleeper 3.

## Recommendation
Allows users to indicate the Sleeper index they wanted when signing the transaction.
