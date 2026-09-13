# [M] NFT can be stuck in user's contract forever

## Summary
Severity: Medium
Reporter: ret2basic.eth
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158
Type: audit-issue

## Details
# NFT can be stuck in user's contract forever

## Summary

OpenZeppelin ERC721 `_mint()` is used for minting. If the user uses a contract instead of EOA and the contract does not support NFT transfer, the NFT bought in the auction can be stuck in the contract forever. Use OpenZeppelin ERC721 `_safeMint()` instead.

## Vulnerability Detail

`MeritDutchAuction.mint()` calls `MeritNFT.mint()`, which calls OpenZeppelin ERC721 `_mint()`:

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63

OpenZeppelin ERC721 `_mint()` does not verify if the receiver can handle NFT. If the user uses a contract for the auction and the contract can't transfer NFT, that NFT can be stuck in the contract forever.

## Impact

NFT can be stuck in user's contract forever.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63

## Tool used

Manual Review

## Recommendation

Use OpenZeppelin ERC721 `_safeMint()` with reentrancy guard.
