# [M] MeritNFT mints tokens using ERC20 _mint instead of _safeMint.

## Summary
Severity: Medium
Reporter: rvdemonk
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158C13-L158C16
Type: audit-issue

## Details
# MeritNFT mints tokens using ERC20 _mint instead of _safeMint.

## Summary

MeritNFT mints tokens using ERC20 _mint instead of _safeMint.

## Vulnerability Detail

Use of _mint means tokens purchased and minted by a smart contracts are not checked to have correctly implemented ERC721Receiver.

## Impact

Merit NFTs could potentially be lost forever in poorly written contracts which mint from the auction but are unable to manage or transfer NFTs. These tokens would be permanently removed from circulation which could hinder the token ecosystem.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158C13-L158C16

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L62C7-L62C7

## Tool used

Manual Review

## Recommendation

Use _safeMint in the mint function of MeritNFT.
