# [M] Minting will start at tokenId = 1 instead of 0

## Summary
Severity: Medium
Reporter: Delvir0
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L156C9-L159C10
Type: audit-issue

## Details
# Minting will start at tokenId = 1 instead of 0

## Summary
Not sure if intended/ overlooked or doesn't matter:

Code uses following loop for minting the amount of nft's
```solidity
for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i + 1, msg.sender);
        }
```
The first tokenId will be `nft.mint(0 + 0 + 1)`
## Vulnerability Detail
x
## Impact
Not sure if it has impact
## Code Snippet
[provided](https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L156C9-L159C10)
## Tool used

Manual Review

## Recommendation
If it's an issue, adjust the calculation or check if it's the first NFT
