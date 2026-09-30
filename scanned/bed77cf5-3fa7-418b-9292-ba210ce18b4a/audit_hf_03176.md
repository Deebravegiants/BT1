# [M] AstariaRouter.commitToLiens will revert if the

## Summary
Severity: Medium
Contest weight: 0.0993
Dataset id: 17738
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The function commitToLiens() will revert in getProtocolFee(), which prevents borrowers from depositing collateral and requesting loans in the protocol. If the protocol fee is enabled by setting feeTo to a non-zero address, then getProtocolFee() will revert because of division-by-zero given that protocolFeeDenominator is 0 without any initialization and no setter (in file()) for setting it. The function commitToLiens() will revert if the protocol fee is enabled thus preventing borrowers from depositing collateral and requesting loans in the protocol thereby failing to bootstrap its core NFT lending functionality.

## Recommendation
Initialize protocol fee numerator and denominator in AstariaRouter and add their setters to file().
