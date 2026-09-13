# [M] Safemint not being used might make some minted NFTs permanently lost

## Summary
Severity: Medium
Reporter: devblixt
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol#L274-L285
Type: audit-issue

## Details
# Safemint not being used might make some minted NFTs permanently lost

## Summary

The MeritDutchAuction contract calls the ERC721 mint() method to mint an NFT to the user. However, this may make some NFTs permanently lost if the user mints the NFT from a smart contract wallet. 

## Vulnerability Detail

The auction contract uses the mint function of MeritNFT to mint the NFT to the user. However, this is not a safe method to mint NFTs and may make users lose NFTs since their wallet might not support ERC721 tokens and they will not receive their money back. 

As per the documentation of EIP-721:

A wallet/broker/auction application MUST implement the wallet interface if it will accept safe transfers.

Reference: https://eips.ethereum.org/EIPS/eip-721

As per the Openzeppelin ERC721 documentation: 

Reference: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol#L274-L285

## Impact

Some users may lose their NFTs

## Code Snippet

The referred code is at https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158

## Tool used

Manual Review

## Recommendation

Use safemint with appropriate nonreentrant guards in the contract for the mint function.
