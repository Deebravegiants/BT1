# [M] A renter can DoS owner from transferring his NFT

## Summary
Severity: Medium
Contest weight: 0.0940
Dataset id: 10483
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocols let users rent their NFTs for a price set by them. Renting the NFT lets the renter use it to
breed with his own NFT and give birth to a new one. Until the NFT is rented the owner can NOT transfer it.
Once the NFT is bred or the rented just decides - it can be returned. The problem is in the rentNFT
function because it lets the renter input the rent time in days. Hence a malicious user can input a large
number of days and NOT breed or return the NFT from rent, intentionally griefing the owner from
transferring it. This also locks the NFT from being bred with other NFTs.

## Recommendation
Add a maximum rent time that can NOT be exceeded - 1 or 2 days for example.
