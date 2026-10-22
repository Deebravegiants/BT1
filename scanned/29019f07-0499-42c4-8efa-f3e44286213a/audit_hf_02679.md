# [H] Incorrect Offset When Setting periodsPaid

## Summary
Severity: High
Contest weight: 0.5495
Dataset id: 14492
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Incorrect offset is referenced when setting periodsPaid variable in the storage.
```solidity
// Update last paid timestamp and periods paid
setUint(bytes32(contractKey + lastPaymentOffset), lastPaymentTime + (periodsToPay * periodLength));
setUint(bytes32(contractKey + periodsPaid), periodsPaid + periodsToPay);
// @audit should be `+ periodsPaidOffset`
```
As a result, an exists variable will be overwritten instead, as periodsPaid will be zero to begin with and existsOffset is also zero.
This could have significant implications to follow, as it will mark and effectively render the contract non-existent.

## Recommendation
Modify code on line [182] to reference the correct offset, i.e. bytes32(contractKey + periodsPaidOffset).
