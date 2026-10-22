# [M] Under certain conditions, direct theft of funds is possible during liquidation

## Summary
Severity: Medium
Contest weight: 0.5399
Dataset id: 3065
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The absence of the notDuringAuction modifier in the AccountV1.deposit() function allows a scenario where a malicious actor can take advantage of the liquidation process. Specifically, a liquidator can bid for assets with a stale share amount that does not consider newly deposited collateral. This results in the liquidator acquiring additional assets for free.

Contrary to withdrawing assets, depositing new collateral into an Account during liquidation is possible because of a missing notDuringAuction modifier.
```solidity

## Recommendation
Apply the notDuringAuction modifier to the deposit function.
```solidity
