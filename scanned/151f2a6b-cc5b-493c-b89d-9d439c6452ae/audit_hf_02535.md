# [H] ETH balances of home and remote messenger can be drained

## Summary
Severity: High
Contest weight: 0.0997
Dataset id: 13535
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
During the executeOrder() function execution, in case the orderId.finalDestinationChainId != block.chainid, the order is outgoing and the recipient of the token is the messenger contract. If the output token after the trade is ETH it will end up as the balance of the HomechainOmnichainMessenger or RemoteOmnichainMessenger contract.

## Recommendation
The recommended fix for the user-facing functions:
