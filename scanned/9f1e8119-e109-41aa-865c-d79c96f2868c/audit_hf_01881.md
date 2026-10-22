# [C] Anyone can mint the entire NFT collection and set genes

## Summary
Severity: Critical
Contest weight: 0.0402
Dataset id: 10458
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol's main concept is around NFTs. One of the contracts is a classic NFT contract with additional features like generations, breeding, genes, and lending the NFTs. The problem however is that the mint function lacks access control and anyone can mint the entire supply of generation 0 to himself, right after deployment. The malicious user could even pass desired genes. The mint function calls _mintSingleNFT() which does the actual minting

## Recommendation
Let only the owner be able to mint. Add the onlyOwner modifier to the NFT_ERC721::mint() function.
