# [M] M-13 | Missing onRecieved Check

## Summary
Severity: Medium
Contest weight: 0.0718
Dataset id: 22069
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Functions createLiquidityPosition and createTraderPosition are minting position NFT's to msg.sender. If the msg.sender is a contract and is not capable of handling NFT related actions and/or is not capable of calling other functions in the system, this position NFT's will stuck at the contract. Considering all actions related to both LP's and Trader's have NFT ownership check, this can lead to locked funds for users.

## Recommendation
Check if the caller of these functions can safely receive ERC721's via checkOnErc721Received.
