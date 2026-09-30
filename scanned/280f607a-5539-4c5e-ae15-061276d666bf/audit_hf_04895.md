# [M] Usage of transfer to send eth might silently

## Summary
Severity: Medium
Contest weight: 0.3732
Dataset id: 22811
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Usage of transfer to send eth might silently fail
Within the contracts, transfer is used to send eth. This is a problem as transfer limits gas consumption to 2300 gas. If the receiving address has a fallback/ receive function which consumes more than 2300 gas, it would cause the transfer to silently fail and the eth will remain within the Maradona contract.
```solidity
payable(receivingUser).transfer(address(this).balance);
```
Loss of funds.

## Recommendation
use .call and check return value
