# [M] Controller doesn't send treasury funds to the

## Summary
Severity: Medium
Contest weight: 0.1062
Dataset id: 19910
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Controller contract sends treasury funds to its own immutable treasury address instead of sending the funds to the one stored in the respective vault contract. Each vault has a treasury address that is assigned on deployment which can also be updated through the factory contract: But, the Controller, responsible for sending the fees to the treasury, uses the immutable treasury address that it was initialized with: It's not possible to have different treasury addresses for different vaults. It's also not possible to update the treasury address of a vault although it has a function to do that. Funds will always be sent to the address the Controller was initialized with.

## Recommendation
The Controller should query the Vault to get the correct treasury address, e.g.:
