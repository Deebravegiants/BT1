# [M] Token 0 never minted

## Summary
Severity: Medium
Reporter: mahdiRostami
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L158
Type: audit-issue

## Details
# Token 0 never minted

## Summary
in mint() function, the function uses for loop for the calculation of the token index, but it starts from 1.
## Vulnerability Detail
[https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L158](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L156-L158)
here, for the first mint, it starts from 1.
## Impact
NFT with index 0 never minted
## Code Snippet
```solidity
        for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i + 1, msg.sender);
```
## Tool used

Manual Review

## Recommendation
in mint() check if mintedBefore is 0 use another calculation:
```solidity
        for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i , msg.sender);
```
