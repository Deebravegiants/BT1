# [M] ERTR-1 | Any Address May Rescue Trapped ETH

## Summary
Severity: Medium
Contest weight: 0.0628
Dataset id: 17862
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The sendWnt function can be called by anyone to collect any ether that may find itself in the ExchangeRouter contract. Meanwhile, the FundReceiver contract that the ExchangeRouter extends stipulates that the controller is the only address that can recover these funds using the recoverNativeToken function.

## Recommendation
If it is not desired that any address be able to rescue trapped ether, consider refactoring the sendWnt logic to be able to safely use the actual amount of ether the user provided. Otherwise, no changes are necessary.
