# [M] Invariant that MeritDutchAuction has MINTER_ROLE can be false

## Summary
Severity: Medium
Reporter: supernova
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L94
Type: audit-issue

## Details
# Invariant that MeritDutchAuction has MINTER_ROLE can be false

## Summary
By reading the code comments, it is understood that `MeritDutchAuction` will be given the `MINTER_ROLE` in the `MeritNFT` contract. 

Then ,  in the `MeritDutchAuction` contract we initialise the `MeritNFT` contract using `setNFT` function .

https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L94

It says `MeritNFT` **must** allow this contract to mint. But it is not checked.

## Vulnerability Detail
Even though  the Auction contract is not authorised , the NFT address will be initialised. And Because it cannot be changed after that, the Auction contract is rendered useless.

## Impact
Auction contract will need to be redeployed.
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L91-L96
## Tool used

Manual Review

## Recommendation
Check if the DutchAuction contract has authorisation to mint in the setNFT function itself.
