# [H] DOS in mint() forever if the owner mint NFTs outside the auction contract

## Summary
Severity: High
Reporter: 0xhuy0512
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L156C1-L159C10
Type: audit-issue

## Details
# DOS in mint() forever if the owner mint NFTs outside the auction contract

## Summary
DOS in `MeritDutchAuction.mint()` forever if the owner mint NFTs outside the auction contract
## Vulnerability Detail
Owner can directly call `MeritNFT.mint()` the contract by gaining `MINTER_ROLE` using `grantRole()`, thus make the function reverted `MeritDutchAuction.mint()` reverted because that tokenId is existed. 
```solidity
        // Interactions
        for(uint256 i = 0; i < amount; i++) {
            // Mint the amount of NFTs to the sender
            nft.mint(mintedBefore + i + 1, msg.sender);
        }
```
## Impact
This can make DOS forever, because `burn()` is not existed

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L156C1-L159C10
## Tool used

Manual Review

## Recommendation
Make the minter role can not change
