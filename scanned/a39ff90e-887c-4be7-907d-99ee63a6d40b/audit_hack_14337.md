# [H] The `setNFT` didn't check if the smart contract has a minter role in nft

## Summary
Severity: High
Reporter: blackhole
Source: https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L91-L96
Type: audit-issue

## Details
# The `setNFT` didn't check if the smart contract has a minter role in nft


## Summary

There is no validation to check if the `MeritDutchAuction` contract has a minter role in that nft or not.
If it doesn't have a minter role, the `mint` function doesn't work properly.
So it needs to check if it has a minter role.


## Vulnerability Detail

https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L91-L96

```solidity
File: src/MeritDutchAuction.sol#L91
    function setNFT(address nft_) external onlyOwner {
        // Can only be set once
        require(address(nft) == address(0), "NFT already set");
        // NFT contract must allow this contract to mint NFTs
        nft = MeritNFT(nft_); // @audit didn't check mintable?
    }
```

## Impact

If it does not have minter role, nobody can mint the nfts using this auction smart contract.

## Code Snippet

https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L91-L96
https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritDutchAuction.sol#L158
https://github.com/sherlock-audit/2023-07-beam-auction/tree/main/dutch-nft/src/MeritNFT.sol#L61
## Tool used

Manual Review

## Recommendation

Recommend adding validation steps to check minter_role in the `setNFT` function

```solidity
File: src/MeritDutchAuction.sol#L91
    function setNFT(address nft_) external onlyOwner {
        // Can only be set once
        require(address(nft) == address(0), "NFT already set");
        // NFT contract must allow this contract to mint NFTs
        nft = MeritNFT(nft_);
        require(nft.hasRole(nft.MINTER_ROLE(), address(this)), "minter role error");
    }
```
