# [M] NFT with ID 0 will not be minted!

## Summary
Severity: Medium
Reporter: Musaka
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169
Type: audit-issue

## Details
# NFT with ID 0 will not be minted!

## Summary
NFT with ID 0 will not be minted!

## Vulnerability Detail
Because of how [`mint`](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L128-L169) calculated the next NFT ID, and more specifically `+1` part, NFT with ID of 0 will never be minted. This means that the collection with nftCap of 10k will have IDs anywhere from 1 to 10 001. 
```jsx
nft.mint(mintedBefore + i + 1, msg.sender);
```
Another issue might be it's [URI implementation](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritNFT.sol#L97-L102), if the team have not made any pictures for ID 10 001.

## Impact
NFT with ID o will not be minted.
## Code Snippet
```jsx
        for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i + 1, msg.sender);
        }
```
## Tool used

Manual Review

## Recommendation
You can store the count as a global variable, and use in this manner.
```jsx
        for(uint256 i = 0; i < amount; i++) {
            nft.mint(nftCount, msg.sender);
            nftCount++;
        }
```
