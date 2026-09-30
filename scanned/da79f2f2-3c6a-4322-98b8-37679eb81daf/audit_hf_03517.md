# [M] GSU-1 | tx.gasprice != 0 Is Fallible

## Summary
Severity: Medium
Contest weight: 0.0537
Dataset id: 19227
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
tx.gasprice != 0 is not a bulletproof means of filtering out non-estimateGas calls. The Keeper can assign a non-zero gasPrice and there has been [discussion](https://github.com/ethereum/go-ethereum/issues/25322) about getting the tx.gasprice to be the basefee even when the gasPrice = 0 in an estimateGas call.

## Recommendation
Use tx.origin as no one can transact from the zero address.
