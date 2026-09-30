# [C] C-02 | Missing Access Control On Settle Function

## Summary
Severity: Critical
Contest weight: 0.1129
Dataset id: 21955
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A user is able to arbitrarily call settle and overwrite any order that is in the queue. By doing this, the
user will not receive funds from their withdrawal.
An attacker could easily time this to repeatedly cause users to have their withdrawn funds locked in
the PerpetualVault contract.

## Recommendation
Implement access control to the function so that it can only be called from the PerpetualVault
contract.
