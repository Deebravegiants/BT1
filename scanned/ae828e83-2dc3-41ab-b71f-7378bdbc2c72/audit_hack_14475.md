# [H] Minting reverts for Auction Contract

## Summary
Severity: High
Reporter: Angry_Mustache_Man
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L27
Type: audit-issue

## Details
# Minting reverts for Auction Contract

## Summary
Due to the presence of `onlyMinter` , minting fails for Auction contract.
## Vulnerability Detail
At several instances of the `MeritDutchAuction.sol` , it is said that the auction contract must be compatible for minting NFT's: 
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L27
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L94
But when calling mint() of NFT contract from Auction contract ,it will revert, because the `mint()` in NFT contract has `onlyMinter` and nowhere in README it says that `Auction Contract` is assigned the role of `MINTER`. Assuming MINTER to be a trusted EOA, the mint() call from Auction Contract will always revert.
## Impact
Reverting of mint() , when called from Auction Contract. 
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L158
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L61C15-L61C15
## Tool used

Manual Review

## Recommendation
Add Auction Contract into the modifier and use `onlyAuctionContractOrMinter` modifier.
