# [M] Discrepancy Between the Documentation and Actual Imple- mentation

## Summary
Severity: Medium
Contest weight: 0.0629
Dataset id: 8740
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The project implementation deviates from its documentation for the following reasons:
• The _mintCheck() function does not verify that the user has enough funds to cover the minting cost.
• The withdraw() function does not check if the contract holds a sufficient amount of tokens/eth.
• The removeBonusToken() function does not delete the claimedToken[token] value.

## Recommendation
It is crucial for the documentation and implementation to completely align.
