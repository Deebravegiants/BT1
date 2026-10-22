# [M] Using ERC721.transferFrom() instead of safeTr

## Summary
Severity: Medium
Contest weight: 0.0870
Dataset id: 17792
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are certain smart contracts that do not support ERC721, using transferFrom() may result in the NFT being sent to such contracts. In unstake(), _to is param from user's input. However, if _to is a contract address that does not support ERC721, the NFT can be frozen in that contract. As per the documentation of EIP-721: A wallet/broker/auction application MUST implement the wallet interface if it will accept safe transfers. Ref: https://eips.ethereum.org/EIPS/eip-721 The NFT may get stuck in the contract that does not support ERC721.

## Recommendation
Consider using safeTransferFrom() instead of transferFrom().
