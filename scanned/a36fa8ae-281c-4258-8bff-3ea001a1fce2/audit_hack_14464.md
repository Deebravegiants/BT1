# [M] Using mint instead of safeMint can freeze funds for receiver contracts that do not support ERC721.

## Summary
Severity: Medium
Reporter: jokr
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol#L274-L285
Type: audit-issue

## Details
# Using mint instead of safeMint can freeze funds for receiver contracts that do not support ERC721.

## Summary

Using mint instead of safeMint can freeze funds for receiver contracts that do not support ERC721.

## Vulnerability Detail

The `MeritDutchAuction.mint` function mints a MeritNFT for the `msg.sender` address. It calls the `MeritNFT.mint` function, which uses the `_mint()` method instead of the `_safeMint()` method. However, if the `msg.sender` address is a contract address that does not  implement `onERC721Received`, the NFT can be frozen in the contract.

As per the documentation of EIP-721:
A wallet/broker/auction application MUST implement the wallet interface if it will accept safe transfers.
Ref: https://eips.ethereum.org/EIPS/eip-721

As per the documentation of ERC721.sol by Openzeppelin
Ref: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol#L274-L285

## Impact

Users could potentially lose their NFTs

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61-L63
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158

## Tool used

Manual Review

## Recommendation

Use `safeMint` instead of `mint` to check received address supports `IERC721Receiver`.
