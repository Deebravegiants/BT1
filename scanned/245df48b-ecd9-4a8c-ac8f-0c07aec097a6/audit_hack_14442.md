# [H] Owner can change the NFT address associated with active auction

## Summary
Severity: High
Reporter: qbs
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91
Type: audit-issue

## Details
# Owner can change the NFT address associated with active auction

## Summary
The setNFT function in the MeritDutchAuction contract allows the owner to change the address of the NFT contract during the auction. 

## Vulnerability Detail
The [setNFT](https://github.com/sherlock-audit/2023-07-beam-auction/blob/main/dutch-nft/src/MeritDutchAuction.sol#L91) function can be called by the contract owner, which according to contest description, is restricted. This allows the owner to change the NFT contract address associated with the auction. A malicious owner is able to change this address during the ongoing auction, resulting in users minting a worthless token instead of the desired one.

## Impact
User can be forced to mint undesirable and worthless token.
## Code Snippet
```solidity
    /// @notice Sets the NFT contract address, can only be called once, only calable by owner
    /// @param nft_ Address of the NFT contract
    function setNFT(address nft_) external onlyOwner {
        // Can only be set once
        require(address(nft) == address(0), "NFT already set");
        // NFT contract must allow this contract to mint NFTs
        nft = MeritNFT(nft_);
    }
   ```
## Tool used

Manual Review

## Recommendation
Disallow changing the NFT address during the active auction.
