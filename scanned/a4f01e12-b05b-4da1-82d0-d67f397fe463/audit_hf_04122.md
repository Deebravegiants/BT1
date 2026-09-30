# [M] GLOBAL-4 | Lack Of Migration Or Extension Mechanisms

## Summary
Severity: Medium
Contest weight: 0.0637
Dataset id: 20582
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The current implementation of the RestEthVault contract lacks a significant part of protocol target functionality. Besides protocol specific functionality it also lacks a means to migrate funds to a new contract or a means to delegate to an operator in the EigenLayer ecosystem. The second aspect may be relevant for any future airdrop or yield increase.

## Recommendation
Until the protocol reaches maturity, in order to support incremental feature development, use an upgradable pattern.
