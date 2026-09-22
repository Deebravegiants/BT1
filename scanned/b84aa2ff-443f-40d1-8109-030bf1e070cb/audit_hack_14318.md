# [M] Every user can mint as many NFTs as they want

## Summary
Severity: Medium
Reporter: gkrastenov
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L143
Type: audit-issue

## Details
# Every user can mint as many NFTs as they want

## Summary
Every user can mint as many NFTs as they want

## Vulnerability Detail
The aim of the constant variable `CAP_PER_ADDRESS` is to prevent users from minting more than 4 NFTs. However, this restriction applies only to a single address. A malicious user can still mint 4 NFTs using their second address and then transfer them to their primary address. In practice, users can use various addresses to interact with the auction and subsequently transfer the NFTs to their primary address. If the user has enough money he can mint all the NFTs and transfer them to a single address.

## Impact
Every user can mint as many NFTs as they want if they have enough money to pay for them. This is possible in the top of the NFTs price and in the bottom. 

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L143

## Tool used

Manual Review

## Recommendation
Block transferring of NFTs when auction is active.
