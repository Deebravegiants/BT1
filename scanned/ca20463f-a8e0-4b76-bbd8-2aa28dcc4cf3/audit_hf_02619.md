# [M] M-3 Mismatched token validation in

## Summary
Severity: Medium
Contest weight: 0.3785
Dataset id: 14142
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
• LPExternalRequestsManager.sol#L425
```
The _completeBurn() method in the LPExternalRequestsManager contract does not contain a validation check to ensure that _item.withdrawalToken is equal to request.token. This vulnerability could lead to a scenario where the off-chain backend mistakenly provides an incorrect _item.withdrawalToken. If such a mistake occurs, the withdrawAvailableCollateral() method may function incorrectly, potentially leading to unintended behavior or loss of funds.

## Recommendation
We recommend ensuring that _item.withdrawalToken matches request.token.
