# [M] Using `_mint()` instead of `_safeMint()` may cause the user's NFT to be frozen in a contract that does not support ERC721

## Summary
Severity: Medium
Reporter: imkapadia
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# Using `_mint()` instead of `_safeMint()` may cause the user's NFT to be frozen in a contract that does not support ERC721

## Summary
In some cases, there are smart contracts that do not support ERC721, and using `_mint()` may result in the loss of NFT for user.

## Vulnerability Detail
The `msg.sender` will mint NFT when `MeritDutchAuction::mint()` is called. Which later calls `MeritNFT::mint()`, This function utilizes `_mint()` instead of `_safeMint()`, which raises concerns regarding the absence of additional safety checks.
However, if `msg.sender` is a contract address that does not support ERC721, the NFT can be frozen in the contract.

OpenZeppelin’s documentation (https://docs.openzeppelin.com/contracts/4.x/api/token/erc721#ERC721-_mint-address-uint256-) also discourages the use of `_mint()` instead use `_safeMint()` whenever possible.

## Impact
Users can lose their NFTs

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63

## Tool used

Manual Review

## Recommendation
Use `_safeMint()` instead of `_mint()` to check received address support for ERC721 implementation.
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol#L245
