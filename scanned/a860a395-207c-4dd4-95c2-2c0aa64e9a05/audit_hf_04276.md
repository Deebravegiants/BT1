# [H] H-08 | Atomic Withdrawal Feature Unusable

## Summary
Severity: High
Contest weight: 0.1600
Dataset id: 21415
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During executeAtomicWithdrawal modifier withOraclePrices is used which when we follow the call trace we will reach the _validatePrices function in Oracle.sol. In this function we check the provider for the given tokens to validate that it is indeed the same provider given by keeper. The problem is, the normal providers for tokens will be the dataStreamProvider while for atomic withdrawals they will be the priceFeedProvider. Hence keeper provided provider won't match this provider in dataStore which will lead to reverts for all atomic withdrawal calls.

## Recommendation
If the action is atomic withdrawal instead of comparing the provided provider with oracleProviderForTokenKey, compare it with isAtomicOracleProviderKey.
