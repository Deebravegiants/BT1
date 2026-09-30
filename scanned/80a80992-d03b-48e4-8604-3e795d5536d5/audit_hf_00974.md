# [H] AccountV1.setApprovedCreditor() doesnt trigger a transfer delay and can be used to steal funds through AccountV1.flashActionByCreditor()

## Summary
Severity: High
Contest weight: 0.7156
Dataset id: 3038
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious owner can set an approvedCreditor before the account transfer and then steal
the funds after the transfer via AccountV1.flashActionByCreditor().

In Arcadia, Accounts are created through the Factory contract by minting an NFT.

```solidity

## Recommendation
Apply the updateActionTimestamp modifier to AccountV1.setApprovedCreditor() to trigger the cool-down period.

```solidity
