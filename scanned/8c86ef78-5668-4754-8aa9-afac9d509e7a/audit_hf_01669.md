# [M] ICE-1 | Centralization Risk

## Summary
Severity: Medium
Contest weight: 0.0589
Dataset id: 9028
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The owner address, 0xa3056090d5583747ef278f3cb6d599aa0e306e64, is not a multi-sig and has potentially dangerous permissions for renounceOwnership, transferOwnership, reserveForGiveaway, setSaleTime, setCost, setMaxMintAmount, setBaseURI, pause, withdraw, and a modified mint execution where the owner can mint Ice Bear NFTs for free.

## Recommendation
Make the owner a multi-sig and/or introduce a timelock for improved community oversight.
