# [H] H-2 Duplicate interactions

## Summary
Severity: High
Contest weight: 0.2096
Dataset id: 9898
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The validateInteractions() function in the Signing.sol#L109 is designed to verify the validity of _interactions before execution. However, a vulnerability exists where an attacker can deduct tokens from a user multiple times by duplicating the same interaction within the _interactions array. The function includes a check: if (amount != _order.baseTokenData.toSupply) revert InvalidAmount(); This condition ensures that the amount matches the signed value _order.baseTokenData.toSupply. However, it does not account for duplicated interactions. By repeating an interaction, an attacker can increase the total amount, causing more tokens to be deducted from the user than intended.

## Recommendation
We recommend revising the validateInteractions function to prevent such manipulations. Specifically, the function should: • Accumulate the Total Amount: Sum the amount from all interactions and compare the cumulative total with _order.baseTokenData.toSupply. This ensures that the total tokens deducted align with the user's signed intent. • Prevent Duplicate Interactions: Implement checks to detect and reject duplicated interactions within the _interactions array.
