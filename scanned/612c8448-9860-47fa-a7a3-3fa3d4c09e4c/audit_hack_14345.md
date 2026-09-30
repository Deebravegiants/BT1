# [M] MeritNFT may be permanently locked when mint it to a contract that does not support ERC721 protocol

## Summary
Severity: Medium
Reporter: kutugu
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L158
Type: audit-issue

## Details
# MeritNFT may be permanently locked when mint it to a contract that does not support ERC721 protocol

## Summary

Users may auction NFT by contract,  when MeritDutchAuction invoke _mint, which will  mint the NFT for the contract. If such contract is not support NFT transfer may result in the NFT being permanently locked.

## Vulnerability Detail

The auction process in question is as follows:
1. User creates contract to auction 4 NFTs
2. The protocol mints NFTs to the contract rather than to the user
3. The contract may not implement the NFT methods, resulting in tokens are permanently locked

## Impact

MeritNFT may be permanently locked when mint it to a contract that does not support ERC721 protocol

## Code Snippet

- https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L158
- https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritNFT.sol#L62

## Tool used

Manual Review

## Recommendation

1. Use _safeMint to ensure that the contract supports NFTs related methods
2. The mint method allows the user to pass in a specified receiver
