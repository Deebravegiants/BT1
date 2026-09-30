# [H] NFT ids do not correspond to their position in the nfts array

## Summary
Severity: High
Contest weight: 0.2445
Dataset id: 10465
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a new NFT is minted it is assigned an id which is pushed in the nfts array. Afterward, NFTs are accessed in that array by id as if the id corresponds to the NFT index in the array. There are two problems with this logic. First, the array index starts at 0 and the first NFT id is 1, because the counter is first incremented and assigned as id to the newly minted NFT after that. Hence it would equal 1. The second issue is with the generation after the initial one. Basically, the protocol mints only the 0th generation which is 150 NFTs and every single one after is minted only by breeding. When a new NFT is born it is assigned an id from a new state variable counter called length, which is initially equal to 150. The problem here is that a NFT can be born before all NFTs from the 0th generation are minted. Hence it would be added to the array and be at an index below 150 but its id would be above 150. This discrepancy between NFT id in the contract and in the array index completely breaks all the protocol logic.

## Recommendation
The most robust solution would be to use a mapping like mapping(uint256 nftId => NFT) to store and access the NFT data.
