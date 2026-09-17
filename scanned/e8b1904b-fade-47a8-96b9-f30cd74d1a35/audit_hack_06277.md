# [M] It is impossible to change ownership of the MintableERC721 if the AuctionHouse contract needs to be replaced

## Summary
Severity: Medium
Reporter: 0x52
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/solidity/MintableERC721.sol#L16-L18
Type: audit-issue

## Details
# It is impossible to change ownership of the MintableERC721 if the AuctionHouse contract needs to be replaced

## Summary

MintableERC721 requires that AuctionHouse is the owner of the contract in order to mint tokens. In the event that AuctionHouse needs to be changed or becomes broken/buggy. There is no way to transfer ownership to a new contract to allow continued minting.

## Vulnerability Detail

See summary.

## Impact

Impossible to change minter of MintableERC721

## Code Snippet

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/solidity/MintableERC721.sol#L16-L18

## Tool used

Manual Review

## Recommendation

I see two solutions:
1) Add a function to AuctionHouse that allows it to transfer the ownership of the NFT
2) Add a minter role to MintableERC721 and use that instead of ownerOnly minting
