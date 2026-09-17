# [M] Owner can `setNFT()` to a wrong address

## Summary
Severity: Medium
Reporter: AlexCzm
Source: https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L91-L96
Type: audit-issue

## Details
# Owner can `setNFT()` to a wrong address

## Summary
Owner can `setNFT()` to a wrong address even at the same time when auction starts. If a wrong address is passed to it, users can mint worthless NFTs.

## Vulnerability Detail

Calling `setNFT` is not restricted at all by `startTime`.  Owner (a malicious one or by mistake) can call it with a wrong contract address when auction starts. In case of hype, users won't have time to check the contract validity and mint garbage nfts.
Since contest readme mentions protocol admin is restricted I rate this as a valid Medium. 

```lang-plaintext
Q: Is the admin/owner of the protocol/contracts TRUSTED or RESTRICTED?
Restricted
```

## Impact
Users may mint worthless nfts.

## Code Snippet
https://github.com/sherlock-audit/2023-07-beam-auction/blob/ab734b575dc3b268de0457c2e3ab0e7d10cd7dd8/dutch-nft/src/MeritDutchAuction.sol#L91-L96

## Tool used

Manual Review

## Recommendation
Allow users enough time to check the nft contract address by introducing a predefined `SET_NFT_BEFORE_START` time after which `nft` storage can't be set.

```solidity
    function setNFT(address nft_) external onlyOwner {
        // Can only be set once
        require(address(nft) == address(0), "NFT already set");
        require(block.timestamp + SET_NFT_BEFORE_START < startTime, "Too close to mint start time" );
        // NFT contract must allow this contract to mint NFTs
        nft = MeritNFT(nft_);
    }
```
