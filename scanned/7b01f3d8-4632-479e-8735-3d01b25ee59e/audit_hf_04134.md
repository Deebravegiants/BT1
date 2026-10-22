# [M] VLT-7 | Yield In Strategies Can Be Stolen

## Summary
Severity: Medium
Contest weight: 0.0694
Dataset id: 20594
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In the event that yield is distributed to a strategy in a single transaction, that yield amount can be vampire attacked by a malicious actor. The actor may deposit into the vault right before the reward is distributed, and then withdraw the gained funds with their Rest shares. These funds end up siphoned from the veritable vault depositors.

## Recommendation
Ensure the vault withdrawal fee is large enough to deter a vampire attack such as this. Additionally be sure to implement a fee for the completeWithdrawEarly function so that the attacker cannot avoid the fee by using the Issuance contract.
