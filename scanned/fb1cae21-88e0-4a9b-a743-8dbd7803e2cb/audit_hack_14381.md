# [M] User can buy at lowest price every time

## Summary
Severity: Medium
Reporter: ubl4nk
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# User can buy at lowest price every time

## Summary

User (or a bot) can trace the mem pool and buy the latest NFT's at lowest price.

## Vulnerability Detail

User knows there are only 10,000 NFT's in auction and also he knows there is a mem pool that can be traced for submitted transactions (it means the user knows how many NFT's have been sold), and he knows one address can only buy 4 NFT's.
According to that the price is decreasing during the auction, so the user can wait until the other users have bought all of the other NFT's and he buys the latest NFT's at the lowest price, or front-runs the latest transaction which is submitted at lowest price.

Note: Another scenario that can be assumed is that all users (or part of them) are familiar with the mem pool and scenario, and all of them will wait until the price reaches to the lowest level (because they know when the auction has started, when it ends, how many NFT's are minted, how many NFT's are available and etc) and in this way, innocent people who bought early are always discriminated against.

## Impact

User can buy at lowest price every time.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L128-L169
https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L106-L124

## Tool used

Manual Review

## Recommendation

Consider some motivation for users to buy earlier.
