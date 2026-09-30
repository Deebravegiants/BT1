# [M] UF-1 | Centralization Risk

## Summary
Severity: Medium
Contest weight: 0.0486
Dataset id: 16215
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The owner address, 0x3e522051a9b1958aa1e828ac24afba4a551df37d, is not a multi-sig and has potentially dangerous permissions for renounceOwnership, transferOwnership, setRoyaltyAddress, setSpiritRouter, updatePaintRouter, setBaseURI, setMintSize, sweepEthToAddress.

## Recommendation
Make the owner a multi-sig and/or introduce a timelock for improved community oversight.
