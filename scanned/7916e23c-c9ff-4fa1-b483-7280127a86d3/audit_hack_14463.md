# [M] A malicious creator has the ability to set up multiple instances of an NFT contract, thereby exploiting collectors when they engage in minting, allowing for the theft of their assets

## Summary
Severity: Medium
Reporter: Phantasmagoria
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91-L96
Type: audit-issue

## Details
# A malicious creator has the ability to set up multiple instances of an NFT contract, thereby exploiting collectors when they engage in minting, allowing for the theft of their assets

## Summary
Owner can set NFT contract multiple times
## Vulnerability Detail
From the screenshot below we know that owner is restricted and that he can set the NFT contract once
![Screenshot from 2023-07-13 15-12-43](https://github.com/sherlock-audit/2023-07-beam-auction-Phantasmagoria13/assets/119745278/56cbc713-173c-4869-bcee-06b9b7b0d006)
But if we take a look at the setNFT function, we can clearly see that the owner can actually set the NFT contract more than once
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91-L96
Attack scenario:
One of the many examples can be that a malicious creator creates a malicious NFT contract with a mint function that mints only one NFT per call, regardless of the value of amount.

Note that mint can be implemented in many malicious ways. This is only one example. Another implementation could simply return the first token ID without performing any minting.
## Impact
The owner of the contract has the ability to set the NFT contract multiple times, which could potentially enable them to steal funds
## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91-L96
## Tool used

Manual Review

## Recommendation
Add restriction to the setNFT function. Something like this:
```solidity
uint256 count = 0;

function setNFT(address nft_) external onlyOwner {
        require(count == 0, "Can only be set once")
        // Can only be set once
        require(address(nft) == address(0), "NFT already set");
        // NFT contract must allow this contract to mint NFTs
        nft = MeritNFT(nft_);
        count += 1
}
```
