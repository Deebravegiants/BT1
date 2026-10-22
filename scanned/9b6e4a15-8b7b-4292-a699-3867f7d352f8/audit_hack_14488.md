# [M] MeritDutchAuction.mint will revert if token is minted directly from MeritNft contract

## Summary
Severity: Medium
Reporter: saian
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L158
Type: audit-issue

## Details
# MeritDutchAuction.mint will revert if token is minted directly from MeritNft contract

## Summary

Minting tokens from MeritDutchAuction contract will revert if another user with a MINTER_ROLE mints a token from MeritNFT contract 

## Vulnerability Detail

Mint function mints tokens sequentially starting from `minted + 1` value to `minted + amount`. But if another user with a MINTER_ROLE mints a token with an id between that value, the function will revert as ERC721._mint reverts for an existing id 

## Impact

Mint funtion will revert and users cannot mint tokens from the auction contract

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L158

```solidity
        // Interactions
        for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i + 1, msg.sender);
        }
```
https://github.com/OpenZeppelin/openzeppelin-contracts/blob/ca822213f2275a14c26167bd387ac3522da67fe9/contracts/token/ERC721/ERC721.sol#L264

```solidity
    function _mint(address to, uint256 tokenId) internal virtual {
        require(to != address(0), "ERC721: mint to the zero address");
        require(!_exists(tokenId), "ERC721: token already minted");
```
## Tool used

Manual Review

## Recommendation

Allow only one user to have minter role
