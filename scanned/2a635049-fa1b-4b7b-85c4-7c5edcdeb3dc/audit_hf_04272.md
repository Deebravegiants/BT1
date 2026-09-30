# [M] M-04 | Missing tokenId Existence Check

## Summary
Severity: Medium
Contest weight: 0.0640
Dataset id: 21306
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a tokenURI function is called in the fallback of the DN404 contract, it is never checked whether the given tokenId exists. According to the recommendation in EIP712, the tokenURI function should throw an error if the tokenId is not a valid NFT. This recommendation is followed in the OpenZeppelin ERC721 implementation contract as well as the ERC721A implementation.

## Recommendation
Check if the given tokenId exists; if it is invalid, revert with a custom error.
