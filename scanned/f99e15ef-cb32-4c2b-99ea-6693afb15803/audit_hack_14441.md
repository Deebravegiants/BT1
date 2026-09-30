# [M] [M-02] `MeritDutchAuction.setNFT()`: Multiple auctions can be made for the same NFT contract

## Summary
Severity: Medium
Reporter: 0xnevi
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol#L276
Type: audit-issue

## Details
# [M-02] `MeritDutchAuction.setNFT()`: Multiple auctions can be made for the same NFT contract

## Summary
Multiple auctions can be made for the same NFT contract, allowing for various problematic scenarios.

## Vulnerability Detail
In `MeritDutchAuction.setNFT()`, there is no checks ensuring multiple auctions are created for the same MerifNFT. There is only a check to ensure that NFT contract is not changed during the auction.

For the same MeritNFT, a NFT owner can flood the auction house with multiple auctions of the same NFT, as long as they are willing to pay gas fees on mainnet. 

This could result in what is known as a [phantom auction](https://right.ly/our-views-and-opinions/going-going-scam/), where a fake auction is created with no intention of allowing minters to mint at all. All other auctions will be completely unusable after the first MeritNFT is minted in any one of the auction created by the owner. Furthermore, malicious owner deploying auction can set prices of minting to be very low and/or decrease at a very fast rate to lure people to mint. Given the high gas fees on mainnet, it can cause substantial lost for users minting on such phantom auctions.

This is due to the `_exists(Id)` [check](https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC721/ERC721.sol#L276) in `ERC721._mint()` which prevents minting of the same tokenId. This results in minters losing gas fees when trying to mint from unusable auctions, given the fact that auctions cannot be cancelled or removed from the auction house. 

This also applies to an unknowing honest NFT owner who **creates 2 or more** separate auctions for the same MeritNFT contract, in which the first auction where a MeritNFT is minted  would render all the other auctions completely unusable.

## Impact
Allowing multiple auctions to be created for the same MeritNFT contract can be problematic (refer to Vulnerability Details section).

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91-L96
```solidity
function setNFT(address nft_) external onlyOwner {
    // Can only be set once
    require(address(nft) == address(0), "NFT already set");
    // NFT contract must allow this contract to mint NFTs
    nft = MeritNFT(nft_);
}
```

## Tool used
Manual Analysis

## Recommendation
Only allow one auction to be created per MeritNFT contract. This can be done by using a factory contract to deploy `MeritDutchAuction` instances and setting a flag for if a auction has been created for the address of a specific MeritNFT contract
