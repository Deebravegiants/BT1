# [M] Minting inconsistencies on FootiumPlayer and

## Summary
Severity: Medium
Contest weight: 0.0475
Dataset id: 19967
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FootiumClub.sol contract when minting uses _mint() instead of _safeMint() which can cause to mint a club to a contract who does not support nfts. On the other hand FootiumPlayer.sol uses _safeMint().
See summary.
FootiumClub.sol might mint a club NFT to a contract that cannot handle nfts.

## Recommendation
Use _safeMint() as in FootiumPlayer.
